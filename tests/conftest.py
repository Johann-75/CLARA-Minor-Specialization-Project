import os
import pandas as pd
import pytest
import duckdb

@pytest.fixture(scope="module")
def db_conn():
    """
    Module scoped fixture that yields a read-only DuckDB connection to clara.db.
    """
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(root, "clara.db")
    conn = duckdb.connect(db_path, read_only=True)
    yield conn
    conn.close()

@pytest.fixture(scope="module")
def synthetic_dataframes():
    """
    Module scoped fixture that loads the 5 synthetic CSVs into a dictionary of DataFrames.
    """
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    folder = os.path.join(root, "data", "synthetic")
    
    dfs = {
        "instances": pd.read_csv(os.path.join(folder, "instances.csv")),
        "metrics": pd.read_csv(os.path.join(folder, "metrics.csv")),
        "security_configs": pd.read_csv(os.path.join(folder, "security_configs.csv")),
        "cost_data": pd.read_csv(os.path.join(folder, "cost_data.csv")),
        "security_events": pd.read_csv(os.path.join(folder, "security_events.csv"))
    }
    yield dfs
