# Command to run: pytest tests/ -v --tb=short

import os
import json
import pandas as pd
import pytest

def test_instances_row_count(synthetic_dataframes):
    """
    Asserts instances count matches configuration.
    """
    from config import SYNTHETIC_INSTANCE_COUNT
    df = synthetic_dataframes["instances"]
    assert len(df) == SYNTHETIC_INSTANCE_COUNT

def test_metrics_row_count(synthetic_dataframes):
    """
    Asserts metrics records count is dynamically based on config parameters.
    """
    from config import SYNTHETIC_INSTANCE_COUNT, SYNTHETIC_DAYS_OF_METRICS
    df = synthetic_dataframes["metrics"]
    assert len(df) == SYNTHETIC_INSTANCE_COUNT * SYNTHETIC_DAYS_OF_METRICS

def test_no_nulls_in_instances(synthetic_dataframes):
    """
    Asserts there are no null values in the instances dataframe.
    """
    df = synthetic_dataframes["instances"]
    assert df.isnull().sum().sum() == 0

def test_cpu_utilization_in_valid_range(synthetic_dataframes):
    """
    Asserts all cpu utilization measurements fall in the range [0.0, 100.0].
    """
    df = synthetic_dataframes["metrics"]
    assert df["cpu_utilization_pct"].min() >= 0.0
    assert df["cpu_utilization_pct"].max() <= 100.0

def test_memory_utilization_in_valid_range(synthetic_dataframes):
    """
    Asserts all memory utilization measurements fall in the range [0.0, 100.0].
    """
    df = synthetic_dataframes["metrics"]
    assert df["memory_utilization_pct"].min() >= 0.0
    assert df["memory_utilization_pct"].max() <= 100.0

def test_no_duplicate_instance_ids(synthetic_dataframes):
    """
    Asserts instance IDs are unique.
    """
    df = synthetic_dataframes["instances"]
    assert df["instance_id"].is_unique

def test_internet_exposed_ratio(synthetic_dataframes):
    """
    Asserts that the count of internet exposed configurations matches expected config ratio.
    """
    from config import SYNTHETIC_INSTANCE_COUNT
    df = synthetic_dataframes["security_configs"]
    exposed_count = int(df["internet_exposed"].sum())
    expected_exposed = int(SYNTHETIC_INSTANCE_COUNT * 0.10)
    assert expected_exposed - 5 <= exposed_count <= expected_exposed + 5

def test_anomaly_manifest_exists_and_has_15_entries():
    """
    Asserts that anomaly_manifest.json exists and tracks exactly 15 injected anomalies.
    """
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    manifest_path = os.path.join(root, "data", "synthetic", "anomaly_manifest.json")
    assert os.path.exists(manifest_path)
    with open(manifest_path, "r") as f:
        data = json.load(f)
    assert len(data) == 15
