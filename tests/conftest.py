import os
import uuid
from datetime import datetime
import pandas as pd
import pytest
import duckdb

@pytest.fixture(scope="session")
def isolated_test_environment(tmp_path_factory):
    """
    Session-scoped fixture providing complete test isolation:
    1. Creates a temporary directory outside the project root for test artifacts.
    2. Generates synthetic CSVs strictly inside the temporary directory.
    3. Builds an isolated test DuckDB database with full schema and loaded data.
    4. Computes risk scores without saving models to disk.
    5. Seeds deterministic fallback recommendations exclusively in the test database.
    6. Monkeypatches runtime database and data access paths to point to the test environment.
    7. Restores all original runtime configurations upon session teardown.
    """
    temp_dir = tmp_path_factory.mktemp("clara_test_env")
    test_csv_dir = os.path.join(str(temp_dir), "synthetic")
    test_db_path = os.path.join(str(temp_dir), "test_clara.db")

    # 1. Generate synthetic data into temporary directory
    from data_generator.generator import SyntheticDataGenerator
    generator = SyntheticDataGenerator()
    generator.export_all(output_dir=test_csv_dir)

    # 2. Initialize schema in temporary database
    from warehouse.db_connection import initialize_schema
    conn = duckdb.connect(test_db_path)
    initialize_schema(conn)

    # 3. Bulk load temporary CSVs into temporary database
    tables_and_csvs = [
        ("cloud_instances", "instances.csv"),
        ("security_configurations", "security_configs.csv"),
        ("metrics_daily", "metrics.csv"),
        ("cost_data", "cost_data.csv"),
        ("security_events", "security_events.csv")
    ]
    for table_name, csv_name in tables_and_csvs:
        csv_path = os.path.join(test_csv_dir, csv_name).replace("\\", "/")
        conn.execute(f"INSERT INTO {table_name} SELECT * FROM read_csv_auto('{csv_path}')")

    # 4. Compute risk scores directly on test DB without persisting models to project root
    import config
    from analytics.anomaly_model import AnomalyDetector
    from analytics.security_model import SecurityRiskModel
    from analytics.cost_model import CostWasteModel

    anomaly_model = AnomalyDetector()
    anomaly_model.train(conn)
    df_anomaly = anomaly_model.predict(conn)

    security_model = SecurityRiskModel()
    df_security = security_model.calculate_risk(conn)

    cost_model = CostWasteModel()
    cost_model.train(conn)
    df_cost = cost_model.predict(conn)

    merged_df = pd.merge(df_security, df_anomaly, on="instance_id")
    merged_df = pd.merge(merged_df, df_cost, on="instance_id")
    merged_df["overall_risk_score"] = (
        merged_df["security_risk_score"] * 0.5 +
        merged_df["anomaly_score"] * 0.3 +
        merged_df["cost_waste_score"] * 0.2
    ).round(4)

    merged_df["score_id"] = [str(uuid.uuid4()) for _ in range(len(merged_df))]
    merged_df["model_version"] = config.MODEL_VERSION
    merged_df["calculated_at"] = datetime.now()

    db_columns = [
        "score_id", "instance_id", "anomaly_score", "security_risk_score",
        "cost_waste_score", "overall_risk_score", "model_version", "calculated_at"
    ]
    df_to_insert = merged_df[db_columns]
    conn.register("temp_risk_scores", df_to_insert)
    conn.execute("INSERT INTO risk_scores SELECT * FROM temp_risk_scores")
    conn.unregister("temp_risk_scores")

    # 5. Seed deterministic fallback recommendations into test DB
    instances = conn.execute("SELECT instance_id FROM cloud_instances LIMIT 5").fetchall()
    sample_recs = [
        (
            str(uuid.uuid4()),
            instances[0][0],
            "cost",
            "High",
            "[Fallback] Rightsize underutilized instance",
            "[Deterministic Fallback] Automated rule-based recommendation generated without external API.",
            "Stop instance | Change instance type to next smaller size | Start instance and verify operations",
            45.50,
            1.0,
            "pending",
            datetime.now(),
            "offline_fallback",
            "deterministic_rule_engine",
            "missing_api_key",
            "Reduces monthly cloud compute spend by right-sizing idle capacity."
        ),
        (
            str(uuid.uuid4()),
            instances[1][0],
            "security",
            "Critical",
            "[Fallback] Restrict public ingress port",
            "[Deterministic Fallback] Automated rule-based recommendation generated without external API.",
            "Review security group rules | Remove 0.0.0.0/0 direct exposure | Apply bastion or VPN ingress",
            0.0,
            0.5,
            "pending",
            datetime.now(),
            "offline_fallback",
            "deterministic_rule_engine",
            "missing_api_key",
            "Eliminates public management port vulnerability and brute-force vector."
        ),
        (
            str(uuid.uuid4()),
            instances[2][0],
            "anomaly",
            "Medium",
            "[Fallback] Investigate telemetry deviation",
            "[Deterministic Fallback] Automated rule-based recommendation generated without external API.",
            "Inspect workload metrics | Check process activity | Monitor disk and memory saturation",
            0.0,
            2.0,
            "pending",
            datetime.now(),
            "offline_fallback",
            "deterministic_rule_engine",
            "missing_api_key",
            "Restores workload behavior to historical baseline variance limits."
        )
    ]
    conn.executemany("""
        INSERT INTO recommendations (
            recommendation_id, instance_id, risk_type, priority, title,
            description, implementation_steps, estimated_savings_usd,
            estimated_effort_hours, status, generated_at,
            generation_source, model_name, fallback_reason, expected_benefit
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_recs)

    # 6. Monkeypatch runtime DB connection and data access path
    import config
    import dashboard.utils.data_access as data_access
    import warehouse.db_connection as db_conn_module
    import streamlit as st

    orig_db_path = data_access.DB_PATH
    orig_get_connection = db_conn_module.get_connection
    orig_get_read_only_conn = data_access.get_read_only_conn
    orig_db_url = config.DATABASE_URL

    data_access.DB_PATH = test_db_path
    config.DATABASE_URL = f"duckdb:///{test_db_path}"

    def test_get_connection(db_path=None):
        if db_path not in (None, "clara.db", test_db_path):
            return duckdb.connect(db_path)
        return conn.cursor()

    db_conn_module.get_connection = test_get_connection
    data_access.get_read_only_conn = lambda: conn.cursor()

    try:
        st.cache_data.clear()
    except Exception:
        pass

    yield {
        "test_db_path": test_db_path,
        "test_csv_dir": test_csv_dir,
        "session_conn": conn,
        "test_get_connection": test_get_connection
    }

    # 7. Teardown: restore original runtime configuration and close test DB
    data_access.DB_PATH = orig_db_path
    data_access.get_read_only_conn = orig_get_read_only_conn
    db_conn_module.get_connection = orig_get_connection
    config.DATABASE_URL = orig_db_url
    try:
        conn.close()
    except Exception:
        pass
    try:
        st.cache_data.clear()
    except Exception:
        pass

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment(isolated_test_environment):
    """
    Session-level autouse fixture activating the isolated test environment.
    """
    return isolated_test_environment

@pytest.fixture(autouse=True)
def patch_test_namespaces(isolated_test_environment):
    """
    Function-level autouse fixture ensuring any test modules that imported get_connection
    directly at file-import time are redirected to the isolated test database connection.
    """
    import sys
    test_get_conn = isolated_test_environment["test_get_connection"]
    if "tests.test_models" in sys.modules:
        sys.modules["tests.test_models"].get_connection = test_get_conn
    if "tests.test_recommendations" in sys.modules:
        sys.modules["tests.test_recommendations"].get_connection = test_get_conn
    if "genai.run_recommendations" in sys.modules:
        sys.modules["genai.run_recommendations"].get_connection = test_get_conn
    yield

@pytest.fixture(scope="session")
def db_conn(isolated_test_environment):
    """
    Session-scoped fixture yielding a DuckDB connection/cursor to the isolated test database.
    """
    cursor = isolated_test_environment["session_conn"].cursor()
    yield cursor
    try:
        cursor.close()
    except Exception:
        pass

@pytest.fixture(scope="session")
def synthetic_dataframes(isolated_test_environment):
    """
    Session-scoped fixture loading the 5 synthetic CSVs from the isolated test directory into DataFrames.
    """
    folder = isolated_test_environment["test_csv_dir"]
    dfs = {
        "instances": pd.read_csv(os.path.join(folder, "instances.csv")),
        "metrics": pd.read_csv(os.path.join(folder, "metrics.csv")),
        "security_configs": pd.read_csv(os.path.join(folder, "security_configs.csv")),
        "cost_data": pd.read_csv(os.path.join(folder, "cost_data.csv")),
        "security_events": pd.read_csv(os.path.join(folder, "security_events.csv"))
    }
    yield dfs
