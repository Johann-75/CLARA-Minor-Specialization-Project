import re
import math
from pathlib import Path
import pytest
import pandas as pd
import duckdb
import plotly.graph_objects as go

from dashboard.utils.risk_tiers import (
    classify_risk_tier,
    get_risk_tier_sql_case,
    RISK_TIER_THRESHOLDS,
    TIER_COLORS,
    TIER_BADGES,
    RISK_WEIGHTS,
    RISK_WEIGHT_SECURITY,
    RISK_WEIGHT_ANOMALY,
    RISK_WEIGHT_COST_WASTE,
    RISK_FORMULA_DISPLAY
)
from dashboard.utils.data_access import (
    get_overview_metrics,
    get_risk_distribution,
    get_top_critical_instances,
    get_recommendations,
    get_cost_trend,
    get_cost_by_instance_type,
    get_fleet_spend_breakdown,
    get_wasteful_instances,
    get_utilization_scatter_data,
    get_port_exposure,
    get_vulnerability_breakdown,
    get_security_events_timeline,
    get_all_security_configs,
    get_cloud_providers,
    get_regions,
    get_audit_metadata
)
from dashboard.components.charts import (
    check_empty,
    risk_distribution_pie,
    cost_trend_line,
    risk_by_region_heatmap,
    port_exposure_bar,
    vulnerability_breakdown_pie,
    security_events_timeline,
    cost_by_type_donut,
    utilization_scatter,
    recommendation_savings_bar,
    utilized_vs_wasted_bar,
    cost_forecast_chart
)

# -----------------------------------------------------------------------------
# 1. Operational Risk Tier Semantics & Boundary Tests
# -----------------------------------------------------------------------------

def test_risk_tier_boundaries_critical():
    """Asserts that scores >= 80.0 are classified strictly as Critical."""
    assert classify_risk_tier(80.0) == "Critical"
    assert classify_risk_tier(80.0001) == "Critical"
    assert classify_risk_tier(99.9) == "Critical"
    assert classify_risk_tier(100.0) == "Critical"

def test_risk_tier_boundaries_high():
    """Asserts that scores in [60.0, 80.0) are classified strictly as High."""
    assert classify_risk_tier(79.999) == "High"
    assert classify_risk_tier(79.9) == "High"
    assert classify_risk_tier(60.0) == "High"
    assert classify_risk_tier(60.0001) == "High"

def test_risk_tier_boundaries_medium():
    """Asserts that scores in [40.0, 60.0) are classified strictly as Medium."""
    assert classify_risk_tier(59.999) == "Medium"
    assert classify_risk_tier(59.9) == "Medium"
    assert classify_risk_tier(40.0) == "Medium"
    assert classify_risk_tier(40.0001) == "Medium"

def test_risk_tier_boundaries_low():
    """Asserts that scores in [0.0, 40.0) are classified strictly as Low."""
    assert classify_risk_tier(39.999) == "Low"
    assert classify_risk_tier(39.9) == "Low"
    assert classify_risk_tier(0.0) == "Low"
    assert classify_risk_tier(0.0001) == "Low"

def test_risk_tier_unknown_on_none():
    """Asserts that None is classified strictly as Unknown, never silently clamped into Low."""
    assert classify_risk_tier(None) == "Unknown"

def test_risk_tier_unknown_on_nan_and_inf():
    """Asserts that NaN and inf values are classified as Unknown."""
    assert classify_risk_tier(float("nan")) == "Unknown"
    assert classify_risk_tier(float("inf")) == "Unknown"
    assert classify_risk_tier(float("-inf")) == "Unknown"

def test_risk_tier_unknown_on_non_numeric():
    """Asserts that non-numeric and unparseable strings are classified as Unknown."""
    assert classify_risk_tier("invalid") == "Unknown"
    assert classify_risk_tier("") == "Unknown"
    assert classify_risk_tier([]) == "Unknown"
    assert classify_risk_tier({}) == "Unknown"

def test_risk_tier_unknown_on_negative_scores():
    """Asserts that negative scores (< 0.0) are classified strictly as Unknown."""
    assert classify_risk_tier(-0.0001) == "Unknown"
    assert classify_risk_tier(-1.0) == "Unknown"
    assert classify_risk_tier(-50.0) == "Unknown"

def test_risk_tier_parses_numeric_strings():
    """Asserts valid numeric string representations parse into correct operational tiers."""
    assert classify_risk_tier("85.5") == "Critical"
    assert classify_risk_tier("70.0") == "High"
    assert classify_risk_tier("45.2") == "Medium"
    assert classify_risk_tier("12.0") == "Low"
    assert classify_risk_tier("-5.0") == "Unknown"

def test_risk_tier_colors_and_badges_include_unknown():
    """Asserts that TIER_COLORS and TIER_BADGES define neutral gray styling for Unknown."""
    assert "Unknown" in TIER_COLORS
    assert TIER_COLORS["Unknown"] == "#94A3B8"  # Slate neutral gray
    assert "Unknown" in TIER_BADGES
    assert TIER_BADGES["Unknown"] == "⚪"

# -----------------------------------------------------------------------------
# 2. SQL and Python Operational Tier Parity Tests
# -----------------------------------------------------------------------------

def test_sql_and_python_tier_parity():
    """
    Asserts complete behavioral parity between Python classify_risk_tier()
    and DuckDB SQL CASE expression across all boundary, edge, and invalid values.
    """
    test_values = [
        -100.0, -1.0, -0.0001,
        0.0, 0.0001, 39.9, 39.999,
        40.0, 40.0001, 59.9, 59.999,
        60.0, 60.0001, 79.9, 79.999,
        80.0, 80.0001, 95.0, 100.0,
        None
    ]
    
    conn = duckdb.connect(":memory:")
    case_expr = get_risk_tier_sql_case("val")
    
    for val in test_values:
        py_tier = classify_risk_tier(val)
        
        if val is None:
            sql_res = conn.execute(f"SELECT {case_expr} FROM (SELECT CAST(NULL AS DOUBLE) AS val)").fetchone()[0]
        else:
            sql_res = conn.execute(f"SELECT {case_expr} FROM (SELECT {val} AS val)").fetchone()[0]
            
        assert py_tier == sql_res, f"Mismatch for value {val}: Python got {py_tier}, SQL got {sql_res}"
        
    conn.close()

# -----------------------------------------------------------------------------
# 3. Production / Dashboard Scoring-Formula Parity Tests
# -----------------------------------------------------------------------------

def test_scoring_formula_parity_against_run_all_models():
    """
    Directly inspects analytics/run_all_models.py to prove that dashboard-displayed
    formula weights match production computation exactly:
    0.5 * Security + 0.3 * Anomaly + 0.2 * Cost Waste
    """
    import os
    proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    run_models_path = os.path.join(proj_root, "analytics", "run_all_models.py")
    
    with open(run_models_path, "r", encoding="utf-8") as f:
        src = f.read()
        
    # Match the production calculation:
    # merged_df["security_risk_score"] * 0.5 + merged_df["anomaly_score"] * 0.3 + merged_df["cost_waste_score"] * 0.2
    assert 'merged_df["security_risk_score"] * 0.5' in src
    assert 'merged_df["anomaly_score"] * 0.3' in src
    assert 'merged_df["cost_waste_score"] * 0.2' in src
    
    # Assert centralized constants match production code
    assert RISK_WEIGHT_SECURITY == 0.5
    assert RISK_WEIGHT_ANOMALY == 0.3
    assert RISK_WEIGHT_COST_WASTE == 0.2
    assert RISK_WEIGHTS["security"] == 0.5
    assert RISK_WEIGHTS["anomaly"] == 0.3
    assert RISK_WEIGHTS["cost_waste"] == 0.2
    assert (RISK_WEIGHT_SECURITY + RISK_WEIGHT_ANOMALY + RISK_WEIGHT_COST_WASTE) == 1.0

def test_dashboard_formula_display_string():
    """Asserts the displayed formula string is accurately formatted."""
    assert RISK_FORMULA_DISPLAY == "0.5 × Security + 0.3 × Anomaly + 0.2 × Cost Waste"

# -----------------------------------------------------------------------------
# 4. Status-Label & Governance Mapping Tests
# -----------------------------------------------------------------------------

def test_accurate_status_label_mapping():
    """Asserts that recommendations priority and status values map accurately."""
    valid_priorities = {"Critical", "High", "Medium", "Low"}
    valid_statuses = {"pending", "approved", "rejected", "archived"}
    
    recs = get_recommendations()
    assert not recs.empty
    for p in recs["priority"].unique():
        assert p in valid_priorities or p == "Unknown"
    for s in recs["status"].unique():
        assert s.lower() in valid_statuses

# -----------------------------------------------------------------------------
# 5. Data Access & Aggregation Tests
# -----------------------------------------------------------------------------

def test_get_overview_metrics_returns_dict_with_expected_keys():
    """Asserts get_overview_metrics returns expected dict metrics."""
    metrics = get_overview_metrics()
    assert isinstance(metrics, dict)
    assert "total_instances" in metrics
    assert "critical_risk_count" in metrics
    assert "high_risk_count" in metrics
    assert "total_monthly_waste_usd" in metrics
    assert "total_potential_savings_usd" in metrics
    assert metrics["total_instances"] > 0


def test_production_overview_metrics_match_submission_claims(monkeypatch):
    """Evaluator-visible totals must come from the immutable production DB."""
    import dashboard.utils.data_access as data_access

    production_db = Path(__file__).resolve().parents[1] / "clara.db"
    monkeypatch.setattr(data_access, "DB_PATH", str(production_db))
    monkeypatch.setattr(
        data_access,
        "get_read_only_conn",
        lambda: duckdb.connect(str(production_db), read_only=True),
    )
    data_access.get_overview_metrics.clear()

    metrics = data_access.get_overview_metrics()

    assert metrics["total_instances"] == 300
    assert metrics["critical_risk_count"] == 1
    assert metrics["high_risk_count"] == 6
    assert metrics["total_monthly_waste_usd"] == pytest.approx(184.58)
    assert metrics["total_potential_savings_usd"] == pytest.approx(220.87)

    data_access.get_overview_metrics.clear()


def test_dashboard_uses_unambiguous_savings_labels():
    """Cost-only savings and all recommendation savings must not be conflated."""
    root = Path(__file__).resolve().parents[1]
    app_source = (root / "dashboard" / "app.py").read_text(encoding="utf-8")
    overview_source = (root / "dashboard" / "pages" / "1_Overview.py").read_text(encoding="utf-8")
    cost_source = (root / "dashboard" / "pages" / "3_Cost_Analysis.py").read_text(encoding="utf-8")

    for source in (app_source, overview_source):
        assert 'label="Cost Recommendation Savings"' in source
        assert 'label="All Recommendation Savings"' in source
        assert 'label="Actionable Monthly Waste"' not in source
        assert 'label="Total Potential Savings"' not in source

    assert 'label="All Recommendation Savings"' in cost_source
    assert 'label="Actionable Potential Savings"' not in cost_source

def test_get_overview_metrics_critical_threshold_semantics(db_conn):
    """
    Asserts that critical_risk_count in get_overview_metrics matches the
    number of rows with overall_risk_score >= 80.0 in the database.
    """
    metrics = get_overview_metrics()
    expected_critical = db_conn.execute(
        "SELECT COUNT(*) FROM risk_scores WHERE overall_risk_score >= 80.0"
    ).fetchone()[0]
    assert metrics["critical_risk_count"] == expected_critical

def test_get_risk_distribution_guarantees_all_tiers_including_unknown():
    """Asserts get_risk_distribution guarantees all 5 categories including Unknown."""
    df = get_risk_distribution()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "risk_category" in df.columns
    assert "count" in df.columns
    
    categories = set(df["risk_category"].tolist())
    assert {"Critical", "High", "Medium", "Low", "Unknown"}.issubset(categories)
    assert df["count"].sum() > 0

def test_get_top_critical_instances_formatting():
    """Asserts get_top_critical_instances returns limited rows with operational_tier."""
    df = get_top_critical_instances(limit=5)
    assert isinstance(df, pd.DataFrame)
    assert len(df) <= 5
    assert "overall_risk_score" in df.columns
    assert "operational_tier" in df.columns
    scores = df["overall_risk_score"].tolist()
    assert scores == sorted(scores, reverse=True)

def test_get_cost_trend_preserves_chronological_order():
    """Asserts get_cost_trend returns dates in ascending chronological order."""
    df = get_cost_trend(days=30)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "date" in df.columns
    assert "daily_cost" in df.columns
    dates = list(df["date"])
    assert dates == sorted(dates)

def test_get_cost_by_instance_type_fleet_coverage():
    """Asserts get_cost_by_instance_type covers multiple instance types with monthly_cost."""
    df = get_cost_by_instance_type()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "instance_type" in df.columns
    assert "monthly_cost" in df.columns
    assert (df["monthly_cost"] >= 0).all()

def test_get_fleet_spend_breakdown():
    """Asserts get_fleet_spend_breakdown returns true fleet totals."""
    df = get_fleet_spend_breakdown()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert "total_monthly_spend" in df.columns
    assert "wasted_spend" in df.columns
    assert "utilized_spend" in df.columns
    total = df["total_monthly_spend"].iloc[0]
    waste = df["wasted_spend"].iloc[0]
    utilized = df["utilized_spend"].iloc[0]
    assert total >= 0
    assert waste >= 0
    assert abs((utilized + waste) - total) < 0.01

def test_get_wasteful_instances_ordering():
    """Asserts get_wasteful_instances returns instances sorted by cost waste score."""
    df = get_wasteful_instances(limit=10)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "cost_waste_score" in df.columns
    scores = df["cost_waste_score"].tolist()
    assert scores == sorted(scores, reverse=True)

def test_get_utilization_scatter_data_fleet_wide():
    """Asserts scatter plot data contains all fleet instances with CPU, Memory, Cost and Risk."""
    df = get_utilization_scatter_data()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "avg_cpu_utilization_pct" in df.columns
    assert "avg_memory_utilization_pct" in df.columns
    assert "avg_daily_cost_usd" in df.columns
    assert "overall_risk_score" in df.columns

def test_get_port_exposure_returns_counts():
    """Asserts port exposure extracts open ports and produces frequency counts."""
    df = get_port_exposure()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "port" in df.columns
    assert "count" in df.columns

def test_get_vulnerability_breakdown_categories():
    """Asserts vulnerability breakdown contains standard vulnerability categories."""
    df = get_vulnerability_breakdown()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 4
    vulns = set(df["vulnerability"].tolist())
    assert "Internet Exposed" in vulns
    assert "Unencrypted Volume" in vulns
    assert "Excessive IAM" in vulns
    assert "Brute-force attempts" in vulns

def test_get_recommendations_schema_and_filters():
    """Asserts get_recommendations handles priority and status filtering with provenance."""
    df_all = get_recommendations()
    assert isinstance(df_all, pd.DataFrame)
    assert "generation_source" in df_all.columns
    assert "model_name" in df_all.columns
    assert "fallback_reason" in df_all.columns

    df_crit = get_recommendations(priority_filter="Critical")
    if not df_crit.empty:
        assert (df_crit["priority"] == "Critical").all()

    df_empty = get_recommendations(status_filter="NonExistentStatus")
    assert isinstance(df_empty, pd.DataFrame)
    assert df_empty.empty
    assert "recommendation_id" in df_empty.columns

def test_filter_by_cloud_provider_and_region():
    """Asserts provider and region filters narrow results correctly."""
    providers = get_cloud_providers()
    assert "All" in providers
    assert len(providers) > 1

    regions = get_regions()
    assert "All" in regions
    assert len(regions) > 1

    prov = providers[1]
    metrics = get_overview_metrics(provider=prov)
    assert metrics["total_instances"] > 0
    assert metrics["total_instances"] <= get_overview_metrics()["total_instances"]

def test_nonexistent_filter_returns_empty_gracefully():
    """Asserts filtering for a non-existent provider yields 0 instances without raising."""
    metrics = get_overview_metrics(provider="NonExistentProvider123")
    assert metrics["total_instances"] == 0
    assert metrics["critical_risk_count"] == 0

    df_crit = get_top_critical_instances(provider="NonExistentProvider123")
    assert df_crit.empty
    assert "instance_id" in df_crit.columns

def test_audit_metadata_contents():
    """Asserts get_audit_metadata returns connection status and timestamps."""
    meta = get_audit_metadata()
    assert isinstance(meta, dict)
    assert meta["total_instances"] > 0
    assert "calc_time_str" in meta
    assert "db_status" in meta

# -----------------------------------------------------------------------------
# 6. Chart Generation & Empty State Smoke Tests
# -----------------------------------------------------------------------------

def test_check_empty_returns_figure_on_empty_df():
    """Asserts check_empty returns a valid Plotly Figure with placeholder annotation."""
    fig, is_empty = check_empty(pd.DataFrame(), "Test Title")
    assert is_empty is True
    assert isinstance(fig, go.Figure)

def test_check_empty_returns_false_on_populated_df():
    """Asserts check_empty returns False when DataFrame has data."""
    df = pd.DataFrame({"a": [1, 2]})
    fig, is_empty = check_empty(df, "Test Title")
    assert is_empty is False
    assert fig is None

def test_all_chart_components_render_figures():
    """Smoke tests all chart generation functions with populated data including Unknown tier."""
    df_risk = pd.DataFrame({
        "risk_category": ["Critical", "High", "Medium", "Low", "Unknown"], 
        "count": [1, 2, 3, 4, 0]
    })
    assert isinstance(risk_distribution_pie(df_risk), go.Figure)

    df_cost = pd.DataFrame({"date": ["2026-10-01", "2026-10-02"], "daily_cost": [100.0, 110.0]})
    assert isinstance(cost_trend_line(df_cost), go.Figure)

    df_region = pd.DataFrame({"cloud_provider": ["AWS", "Azure"], "region": ["us-east-1", "eastus"], "avg_risk_score": [50.0, 60.0]})
    assert isinstance(risk_by_region_heatmap(df_region), go.Figure)

    df_port = pd.DataFrame({"port": ["80", "443"], "count": [10, 20]})
    assert isinstance(port_exposure_bar(df_port), go.Figure)

    df_vuln = pd.DataFrame({"vulnerability": ["Internet Exposed", "Excessive IAM"], "count": [5, 10]})
    assert isinstance(vulnerability_breakdown_pie(df_vuln), go.Figure)

    df_events = pd.DataFrame({"event_id": ["e1"], "severity": ["critical"], "timestamp": ["2026-10-01 10:00:00"]})
    assert isinstance(security_events_timeline(df_events), go.Figure)

    df_type = pd.DataFrame({"instance_type": ["t3.micro", "m5.large"], "monthly_cost": [50.0, 200.0]})
    assert isinstance(cost_by_type_donut(df_type), go.Figure)

    df_scatter = pd.DataFrame({
        "instance_id": ["i-1"],
        "avg_cpu_utilization_pct": [25.0],
        "avg_memory_utilization_pct": [40.0],
        "avg_daily_cost_usd": [5.0],
        "overall_risk_score": [55.0]
    })
    assert isinstance(utilization_scatter(df_scatter), go.Figure)

    df_recs = pd.DataFrame({
        "title": ["Rightsize Idle Instance"],
        "estimated_savings_usd": [50.0],
        "priority": ["High"]
    })
    assert isinstance(recommendation_savings_bar(df_recs), go.Figure)

    df_spend = pd.DataFrame({"total_monthly_spend": [1000.0], "wasted_spend": [200.0], "utilized_spend": [800.0]})
    assert isinstance(utilized_vs_wasted_bar(df_spend), go.Figure)

    assert isinstance(cost_forecast_chart(df_cost, forecast_days=30), go.Figure)
