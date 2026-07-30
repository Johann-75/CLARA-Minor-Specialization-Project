import pytest
import pandas as pd
from dashboard.utils.data_access import (
    get_overview_metrics,
    get_risk_distribution,
    get_top_critical_instances,
    get_recommendations
)

# Note: The data_access module functions are decorated with @st.cache_data.
# When executed outside of a running Streamlit server (such as during pytest),
# Streamlit will print a fallback warning ("No runtime found, using MemoryCacheStorageManager")
# but the functions will execute and return correct cached results successfully without raising exceptions.

def test_get_overview_metrics_returns_dict_with_expected_keys():
    """
    Smoke test verifying get_overview_metrics returns expected dict metrics.
    """
    metrics = get_overview_metrics()
    assert isinstance(metrics, dict)
    assert "total_instances" in metrics
    assert "critical_risk_count" in metrics
    assert "total_monthly_waste_usd" in metrics
    assert "total_potential_savings_usd" in metrics

def test_get_risk_distribution_returns_dataframe():
    """
    Smoke test verifying get_risk_distribution returns expected pandas DataFrame columns.
    """
    df = get_risk_distribution()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "risk_category" in df.columns
    assert "count" in df.columns

def test_get_top_critical_instances_returns_10_rows():
    """
    Smoke test verifying get_top_critical_instances limits row outputs.
    """
    df = get_top_critical_instances(limit=10)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 10
    assert "overall_risk_score" in df.columns

def test_get_recommendations_returns_dataframe():
    """
    Smoke test verifying get_recommendations returns recommendations fields.
    """
    df = get_recommendations()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "recommendation_id" in df.columns
    assert "priority" in df.columns
    assert "estimated_savings_usd" in df.columns
