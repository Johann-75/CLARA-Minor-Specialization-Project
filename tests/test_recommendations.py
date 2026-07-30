import pytest
import pandas as pd
from unittest.mock import patch
from genai.recommendation_engine import RecommendationEngine

@patch('genai.recommendation_engine.GeminiClient')
def test_recommendation_engine_structure(mock_client_class):
    """
    Verifies that RecommendationEngine returns expected properties in recommendation record.
    """
    # Setup mock instance and its generate_json method
    mock_client = mock_client_class.return_value
    mock_client.generate_json.return_value = {
        "title": "Rightsize Instance",
        "description": "This instance is underutilized. Rightsize it to save cost.",
        "priority": "High",
        "implementation_steps": ["Stop instance", "Change instance type", "Start instance"],
        "estimated_effort_hours": 1.0,
        "estimated_downtime_minutes": 10
    }

    engine = RecommendationEngine()
    
    # Mock row payload representing cost waste instance details
    mock_row = {
        "instance_id": "i-test-genai",
        "cloud_provider": "AWS",
        "region": "us-east-1",
        "instance_type": "m5.large",
        "security_risk_score": 20.0,
        "anomaly_score": 15.0,
        "cost_waste_score": 85.0,
        "internet_exposed": False,
        "encryption_enabled": True,
        "iam_permission_level": "least-privilege",
        "failed_logins_7d": 0,
        "daily_cost_usd": 4.50,
        "utilization_pct": 2.5
    }
    
    # Generate recommendation for cost type
    rec = engine.generate_recommendation(mock_row, "cost")
    
    assert isinstance(rec, dict)
    assert rec["instance_id"] == "i-test-genai"
    assert rec["risk_type"] == "cost"
    assert "title" in rec
    assert "description" in rec
    assert "priority" in rec
    assert "implementation_steps" in rec
    assert isinstance(rec["implementation_steps"], list)
    assert rec["estimated_savings_usd"] > 0.0

def test_recommendations_table_has_rows(db_conn):
    """
    Asserts recommendations table is populated with at least one record.
    """
    count = db_conn.execute("SELECT COUNT(*) FROM recommendations").fetchone()[0]
    assert count > 0

def test_recommendations_priority_values_valid(db_conn):
    """
    Asserts every row's priority belongs to the allowed domain [Critical, High, Medium, Low].
    """
    df = db_conn.execute("SELECT DISTINCT priority FROM recommendations").fetchdf()
    valid_priorities = {"Critical", "High", "Medium", "Low"}
    for p in df["priority"]:
        assert p in valid_priorities

def test_recommendations_have_titles_and_descriptions(db_conn):
    """
    Asserts title and description columns contain no NULLs or blank spaces.
    """
    df = db_conn.execute("SELECT title, description FROM recommendations").fetchdf()
    assert df.isnull().sum().sum() == 0
    for col in df.columns:
        assert (df[col].str.strip() == "").sum() == 0

def test_every_recommendation_links_to_valid_instance(db_conn):
    """
    Asserts referential integrity check: all linked instance IDs exist in cloud_instances.
    """
    df = db_conn.execute("""
        SELECT r.instance_id, ci.instance_id AS linked_id
        FROM recommendations r
        LEFT JOIN cloud_instances ci ON r.instance_id = ci.instance_id
    """).fetchdf()
    assert df["linked_id"].isnull().sum() == 0
