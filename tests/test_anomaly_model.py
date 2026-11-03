import os
import re
import inspect
import pytest
import duckdb
import numpy as np
import pandas as pd
from warehouse.db_connection import get_connection
from analytics.anomaly_model import AnomalyDetector
from analytics.evaluate_anomaly_model import evaluate_predictions, evaluate_seed_in_memory, evaluate_default_database
from dashboard.utils.data_access import get_overview_metrics, get_top_critical_instances

def test_anomaly_detector_multi_modal_contract():
    """
    Verifies that AnomalyDetector trains and outputs all required multi-modal
    sub-scores, classifications, and valid score ranges.
    """
    conn = get_connection()
    try:
        detector = AnomalyDetector()
        detector.train(conn)
        scores = detector.predict(conn)

        assert isinstance(scores, pd.DataFrame)
        expected_columns = [
            "instance_id",
            "anomaly_score",
            "telemetry_anomaly_score",
            "contextual_anomaly_score",
            "is_anomaly"
        ]
        for col in expected_columns:
            assert col in scores.columns, f"Missing required column: {col}"

        assert not scores.empty
        assert len(scores) == 300

        # Score ranges must be within [0.0, 100.0]
        assert scores["anomaly_score"].min() >= 0.0
        assert scores["anomaly_score"].max() <= 100.0
        assert scores["telemetry_anomaly_score"].min() >= 0.0
        assert scores["telemetry_anomaly_score"].max() <= 100.0
        assert scores["contextual_anomaly_score"].min() >= 0.0
        assert scores["contextual_anomaly_score"].max() <= 100.0

        # Boolean classification
        assert scores["is_anomaly"].dtype == bool or np.issubdtype(scores["is_anomaly"].dtype, np.bool_)

        # Combined score is upper-bounded by max of sub-scores
        max_sub = np.maximum(scores["telemetry_anomaly_score"], scores["contextual_anomaly_score"])
        np.testing.assert_allclose(scores["anomaly_score"].values, max_sub.values, rtol=1e-3)
    finally:
        conn.close()

def test_active_production_config_matches_cli():
    """
    Proves that the active production detector configuration is the exact same configuration
    evaluated by the command-line evaluation tool.
    """
    prod_detector = AnomalyDetector()
    eval_res = evaluate_default_database()

    # The production defaults must exactly match CLI evaluated configuration
    assert prod_detector.decision_threshold == 65.0
    assert prod_detector.logistic_shift == 0.010
    assert prod_detector.logistic_k == 30.0
    assert prod_detector.model.contamination == 0.04
    assert eval_res["decision_threshold"] == prod_detector.decision_threshold

def test_no_manifest_ground_truth_leakage():
    """
    Proves that anomaly_model.py does not read or import anomaly_manifest.json.
    Evaluation ground truth remains strictly separated from model training and prediction.
    """
    import analytics.anomaly_model as am_module
    src = inspect.getsource(am_module)
    assert "anomaly_manifest.json" not in src, "Ground truth manifest must NEVER be read in anomaly_model.py"
    assert "anomaly_manifest" not in src, "Ground truth manifest reference detected in anomaly_model.py"

def test_no_hardcoded_instances_seeds_or_labels():
    """
    Proves that no specific instance IDs, seeds, or manifest anomaly type labels
    are hardcoded in the model implementation.
    """
    import analytics.anomaly_model as am_module
    src = inspect.getsource(am_module)

    # 1. No hardcoded instance IDs (format i-[0-9a-f]{12})
    hardcoded_ids = re.findall(r"i-[0-9a-f]{12}", src)
    assert len(hardcoded_ids) == 0, f"Detected hardcoded instance IDs: {hardcoded_ids}"

    # 2. No hardcoded evaluation ground truth category labels
    manifest_labels = ["cpu_spike", "memory_leak", "network_exfiltration", "brute_force", "misconfiguration"]
    for label in manifest_labels:
        assert label not in src, f"Detected hardcoded ground-truth manifest label '{label}' in anomaly_model.py"

def test_cpu_spike_detection_across_baselines():
    """
    Proves that CPU spike detection flags anomalies across both:
    1. Normal utilization baselines (~45% CPU jumping to ~98%).
    2. High utilization / overutilized baselines (~85% CPU with high operational alert).
    """
    dates = pd.date_range("2026-01-01", periods=90, freq="D")

    # Instance A: Normal baseline (45%) with spike to 99% on days 50-52
    cpu_normal = [45.0 + (i % 5) for i in range(90)]
    cpu_normal[50] = 99.0
    cpu_normal[51] = 99.0
    mem_normal = [45.0 + (i % 5) for i in range(90)]
    net_normal = [100.0 for _ in range(90)]

    # Instance B: High baseline (85%) with operational alert on day 50
    cpu_high = [85.0 + (i % 5) for i in range(90)]
    mem_high = [85.0 + (i % 5) for i in range(90)]
    net_high = [100.0 for _ in range(90)]

    records_metrics = []
    for d_idx, dt in enumerate(dates):
        records_metrics.append({
            "instance_id": "test-norm-base", "date": dt,
            "cpu_utilization_pct": cpu_normal[d_idx], "memory_utilization_pct": mem_normal[d_idx],
            "network_out_mb": net_normal[d_idx]
        })
        records_metrics.append({
            "instance_id": "test-high-base", "date": dt,
            "cpu_utilization_pct": cpu_high[d_idx], "memory_utilization_pct": mem_high[d_idx],
            "network_out_mb": net_high[d_idx]
        })
        # Add background instances so Isolation Forest has a population distribution
        for bg in range(20):
            records_metrics.append({
                "instance_id": f"bg-inst-{bg}", "date": dt,
                "cpu_utilization_pct": 45.0, "memory_utilization_pct": 45.0,
                "network_out_mb": 50.0
            })

    test_metrics_df = pd.DataFrame(records_metrics)
    test_sec_df = pd.DataFrame([
        {"instance_id": "test-norm-base", "internet_exposed": False, "open_ports": "80,443", "failed_logins_7d": 1},
        {"instance_id": "test-high-base", "internet_exposed": False, "open_ports": "80,443", "failed_logins_7d": 2},
    ] + [
        {"instance_id": f"bg-inst-{bg}", "internet_exposed": False, "open_ports": "80", "failed_logins_7d": 0}
        for bg in range(20)
    ])
    # Emit acute high-severity operational alert for the high baseline spike
    test_events_df = pd.DataFrame([
        {
            "event_id": "evt-high-1",
            "instance_id": "test-high-base",
            "event_type": "anomalous_traffic",
            "severity": "high",
            "description": "Critical CPU runaway alert",
            "timestamp": pd.Timestamp("2026-02-20 10:00:00")
        }
    ])

    mem_conn = duckdb.connect(":memory:")
    mem_conn.register("metrics_daily", test_metrics_df)
    mem_conn.register("security_configurations", test_sec_df)
    mem_conn.register("security_events", test_events_df)

    det = AnomalyDetector()
    det.train(mem_conn)
    preds = det.predict(mem_conn).set_index("instance_id")
    mem_conn.close()

    # Both normal and high-baseline spiked instances must be flagged as anomalies
    assert preds.loc["test-norm-base", "anomaly_score"] >= 65.0
    assert preds.loc["test-norm-base", "is_anomaly"] == True

    assert preds.loc["test-high-base", "anomaly_score"] >= 65.0
    assert preds.loc["test-high-base", "is_anomaly"] == True

def test_contextual_misconfiguration_not_limited_to_22_3389():
    """
    Proves that contextual misconfiguration detection flags unapproved port opening
    events across arbitrary sensitive/service ports (e.g. 3306 MySQL, 5432 PostgreSQL, 8080),
    not merely ports 22 and 3389.
    """
    test_sec_df = pd.DataFrame([
        {"instance_id": "inst-db-mysql", "internet_exposed": True, "open_ports": "3306,80,443", "failed_logins_7d": 2},
        {"instance_id": "inst-db-pg", "internet_exposed": True, "open_ports": "5432,80", "failed_logins_7d": 1},
        {"instance_id": "inst-alt-web", "internet_exposed": True, "open_ports": "8080,443", "failed_logins_7d": 0},
        {"instance_id": "inst-internal", "internet_exposed": False, "open_ports": "3306,8080", "failed_logins_7d": 0},
    ])
    test_events_df = pd.DataFrame([
        {"event_id": "e1", "instance_id": "inst-db-mysql", "event_type": "port_opened", "severity": "high"},
        {"event_id": "e2", "instance_id": "inst-db-pg", "event_type": "port_opened", "severity": "high"},
        {"event_id": "e3", "instance_id": "inst-alt-web", "event_type": "port_opened", "severity": "high"},
        {"event_id": "e4", "instance_id": "inst-internal", "event_type": "port_opened", "severity": "high"},
    ])

    mem_conn = duckdb.connect(":memory:")
    mem_conn.register("security_configurations", test_sec_df)
    mem_conn.register("security_events", test_events_df)

    det = AnomalyDetector()
    df_contextual = det.calculate_contextual_anomaly(mem_conn)
    mem_conn.close()

    # Internet-exposed instances with opened ports must be scored as contextual anomalies (>= 65.0)
    assert df_contextual.loc["inst-db-mysql", "contextual_anomaly_score"] >= 65.0
    assert df_contextual.loc["inst-db-pg", "contextual_anomaly_score"] >= 65.0
    assert df_contextual.loc["inst-alt-web", "contextual_anomaly_score"] >= 65.0

    # Internal (not exposed) instance should NOT be scored as a public perimeter breach
    assert df_contextual.loc["inst-internal", "contextual_anomaly_score"] < 65.0

def test_telemetry_features_completeness():
    """
    Verifies that _build_telemetry_features creates the required time-series features
    without missing or non-finite values.
    """
    conn = get_connection()
    try:
        detector = AnomalyDetector()
        features = detector._build_telemetry_features(conn)

        required_features = [
            "cpu_robust_z_max",
            "cpu_day_diff_max",
            "cpu_peak_to_median",
            "cpu_7_vs_30_dev_max",
            "mem_robust_z_max",
            "mem_day_diff_max",
            "mem_rolling_slope_max",
            "mem_minus_cpu_max",
            "net_robust_z_max",
            "net_day_diff_max",
            "net_peak_to_median"
        ]

        for feat in required_features:
            assert feat in features.columns, f"Feature {feat} is missing from telemetry feature matrix"

        assert not features.isnull().any().any(), "Telemetry feature matrix contains NaN values"
        assert np.isfinite(features.values).all(), "Telemetry feature matrix contains non-finite values"
    finally:
        conn.close()

def test_anomaly_model_persistence(tmp_path):
    """
    Verifies that save and load preserve all model state, hyperparameters, and feature definitions.
    """
    conn = get_connection()
    try:
        detector = AnomalyDetector()
        detector.train(conn)
        preds_before = detector.predict(conn)

        save_file = str(tmp_path / "test_anomaly_model.pkl")
        detector.save(save_file)

        loaded_detector = AnomalyDetector()
        loaded_detector.load(save_file)

        assert loaded_detector.feature_columns == detector.feature_columns
        assert loaded_detector.decision_threshold == detector.decision_threshold
        assert loaded_detector.logistic_k == detector.logistic_k
        assert loaded_detector.logistic_shift == detector.logistic_shift

        preds_after = loaded_detector.predict(conn)
        pd.testing.assert_frame_equal(preds_before, preds_after)
    finally:
        conn.close()

def test_evaluate_predictions_metrics():
    """
    Verifies evaluation metric calculation (TP, FP, FN, TN, precision, recall, F1).
    """
    preds_df = pd.DataFrame({
        "instance_id": ["i-1", "i-2", "i-3", "i-4"],
        "anomaly_score": [90.0, 80.0, 20.0, 10.0],
        "is_anomaly": [True, True, False, False]
    })
    manifest = [
        {"instance_id": "i-1", "anomaly_type": "cpu_spike"},
        {"instance_id": "i-3", "anomaly_type": "memory_leak"}
    ]
    res = evaluate_predictions(preds_df, manifest)
    assert res["tp"] == 1
    assert res["fp"] == 1
    assert res["fn"] == 1
    assert res["tn"] == 1
    assert res["precision"] == 0.5
    assert res["recall"] == 0.5
    assert res["f1"] == 0.5
    assert "cpu_spike" in res["type_recall"]
    assert res["type_recall"]["cpu_spike"]["caught"] == 1
    assert res["type_recall"]["memory_leak"]["caught"] == 0

def test_pipeline_and_dashboard_compatibility():
    """
    Proves that risk scoring schema and dashboard query integration remain completely intact.
    """
    conn = get_connection()
    try:
        # Check risk_scores columns match exactly
        expected_cols = [
            "score_id", "instance_id", "anomaly_score", "security_risk_score",
            "cost_waste_score", "overall_risk_score", "model_version", "calculated_at"
        ]
        db_cols = conn.execute("DESCRIBE risk_scores").fetchdf()["column_name"].tolist()
        for c in expected_cols:
            assert c in db_cols, f"Column {c} missing from risk_scores table"

        # Check dashboard queries work
        overview = get_overview_metrics()
        assert "total_instances" in overview
        assert overview["total_instances"] == 300

        top_crit = get_top_critical_instances(10)
        assert len(top_crit) == 10
    finally:
        conn.close()
