import pytest
import pandas as pd
from warehouse.db_connection import get_connection
from analytics.anomaly_model import AnomalyDetector
from analytics.security_model import SecurityRiskModel
from analytics.cost_model import CostWasteModel

def test_anomaly_detector():
    """
    Verifies that AnomalyDetector trains and predicts correctly using database connection.
    """
    conn = get_connection()
    try:
        detector = AnomalyDetector()
        detector.train(conn)
        scores = detector.predict(conn)
        
        assert isinstance(scores, pd.DataFrame)
        assert "instance_id" in scores.columns
        assert "anomaly_score" in scores.columns
        assert not scores.empty
        assert scores["anomaly_score"].min() >= 0.0
        assert scores["anomaly_score"].max() <= 100.0
    finally:
        conn.close()

def test_security_risk_model():
    """
    Verifies that SecurityRiskModel calculates rule-based security scores correctly from database.
    """
    conn = get_connection()
    try:
        model = SecurityRiskModel()
        scores = model.calculate_risk(conn)
        
        assert isinstance(scores, pd.DataFrame)
        assert "instance_id" in scores.columns
        assert "security_risk_score" in scores.columns
        assert "contributing_factors" in scores.columns
        assert not scores.empty
        assert scores["security_risk_score"].min() >= 0.0
        assert scores["security_risk_score"].max() <= 100.0
    finally:
        conn.close()

def test_cost_waste_model():
    """
    Verifies that CostWasteModel trains and predicts cost waste clusters correctly using database connection.
    """
    conn = get_connection()
    try:
        model = CostWasteModel()
        model.train(conn)
        predictions = model.predict(conn)
        
        assert isinstance(predictions, pd.DataFrame)
        assert "instance_id" in predictions.columns
        assert "cost_waste_score" in predictions.columns
        assert "estimated_monthly_savings_usd" in predictions.columns
        assert not predictions.empty
        assert predictions["cost_waste_score"].min() >= 0.0
        assert predictions["cost_waste_score"].max() <= 100.0
    finally:
        conn.close()

def test_risk_scores_table_populated(db_conn):
    """
    Asserts risk_scores table has exactly 300 entries.
    """
    count = db_conn.execute("SELECT COUNT(*) FROM risk_scores").fetchone()[0]
    assert count == 300

def test_risk_scores_in_valid_range(db_conn):
    """
    Asserts security, anomaly, cost waste, and overall risk scores are within [0.0, 100.0].
    """
    df = db_conn.execute("SELECT security_risk_score, anomaly_score, cost_waste_score, overall_risk_score FROM risk_scores").fetchdf()
    for col in df.columns:
        assert df[col].min() >= 0.0
        assert df[col].max() <= 100.0

def test_no_nulls_in_risk_scores(db_conn):
    """
    Asserts that there are no null fields in the risk_scores table.
    """
    df = db_conn.execute("SELECT * FROM risk_scores").fetchdf()
    assert df.isnull().sum().sum() == 0

def test_high_security_score_correlates_with_exposure(db_conn):
    """
    Asserts that exposed instances have a higher average security risk score than non-exposed.
    """
    query = """
        SELECT sc.internet_exposed, AVG(rs.security_risk_score) AS avg_score
        FROM security_configurations sc
        JOIN risk_scores rs ON sc.instance_id = rs.instance_id
        GROUP BY sc.internet_exposed
    """
    df = db_conn.execute(query).fetchdf()
    
    avg_exposed = df[df["internet_exposed"] == True]["avg_score"].iloc[0]
    avg_not_exposed = df[df["internet_exposed"] == False]["avg_score"].iloc[0]
    
    assert avg_exposed > avg_not_exposed

def test_cost_waste_correlates_with_low_utilization(db_conn):
    """
    Asserts that underutilized instances have a higher average cost waste score.
    """
    query = """
        SELECT 
            rs.cost_waste_score, 
            AVG(m.cpu_utilization_pct) AS avg_cpu
        FROM risk_scores rs
        JOIN metrics_daily m ON rs.instance_id = m.instance_id
        GROUP BY rs.instance_id, rs.cost_waste_score
    """
    df = db_conn.execute(query).fetchdf()
    
    low_util_scores = df[df["avg_cpu"] < 10.0]["cost_waste_score"]
    high_util_scores = df[df["avg_cpu"] > 50.0]["cost_waste_score"]
    
    assert low_util_scores.mean() > high_util_scores.mean()
