import uuid
from datetime import datetime
import duckdb
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from genai.recommendation_engine import RecommendationEngine
from genai.insights_engine import InsightsEngine
from genai.gemini_client import GeminiClient, classify_error, sanitize_text
from genai.schemas import GeminiRecommendationBatchResponse, GeminiRecommendationItem
from genai.run_recommendations import main as run_recs_main
from warehouse.db_connection import get_connection, migrate_schema

def test_live_gemini_success(db_conn):
    """
    Test 1: Verifies that a successful Gemini structured response produces records
    with generation_source='gemini', model_name='gemini-3.8-flash', and fallback_reason=None.
    """
    engine = RecommendationEngine(api_key="mock_key")
    target_instances = db_conn.execute("SELECT instance_id FROM risk_scores ORDER BY overall_risk_score DESC LIMIT 2").fetchall()
    inst_1, inst_2 = target_instances[0][0], target_instances[1][0]

    mock_batch = GeminiRecommendationBatchResponse(
        recommendations=[
            GeminiRecommendationItem(
                instance_id=inst_1,
                priority="Critical",
                title="Isolate internet exposed host",
                explanation="Security risk score is elevated with exposed remote ports.",
                recommended_action="Remove public SG ingress rule and route via VPN.",
                expected_benefit="Mitigates perimeter vulnerability.",
                source="gemini",
                model_name="gemini-3.8-flash",
                estimated_savings_usd=0.0,
                estimated_effort_hours=1.5
            ),
            GeminiRecommendationItem(
                instance_id=inst_2,
                priority="High",
                title="Downsize idle instance",
                explanation="CPU utilization is below 5% for 30 consecutive days.",
                recommended_action="Downsize instance family to t3.micro.",
                expected_benefit="Saves $45 monthly.",
                source="gemini",
                model_name="gemini-3.8-flash",
                estimated_savings_usd=45.0,
                estimated_effort_hours=1.0
            )
        ]
    )

    with patch.object(engine.client, "generate_structured", return_value=(mock_batch, None)):
        recs = engine.generate_for_all_high_risk(db_conn, threshold=0.0, limit=2)
        assert len(recs) == 2
        for r in recs:
            assert r["generation_source"] == "gemini"
            assert r["model_name"] == "gemini-3.8-flash"
            assert r["fallback_reason"] is None
            assert r["priority"] in ["Critical", "High", "Medium", "Low"]

def test_missing_api_key_triggers_offline_fallback(db_conn):
    """
    Test 2: Verifies that unconfigured GEMINI_API_KEY triggers deterministic offline fallback
    with generation_source='offline_fallback' and fallback_reason='missing_api_key'.
    """
    engine = RecommendationEngine(api_key="")
    recs = engine.generate_for_all_high_risk(db_conn, threshold=0.0, limit=3)
    assert len(recs) > 0
    for r in recs:
        assert r["generation_source"] == "offline_fallback"
        assert r["model_name"] == "deterministic_rule_engine"
        assert r["fallback_reason"] == "missing_api_key"
        assert len(r["title"]) > 0
        assert len(r["description"]) > 0
        assert isinstance(r["implementation_steps"], list)

def test_auth_failure_triggers_error_fallback(db_conn):
    """
    Test 3: Verifies that 401/403 auth error falls back gracefully with fallback_reason='auth_error'.
    """
    engine = RecommendationEngine(api_key="mock_invalid_key")
    with patch.object(engine.client, "generate_structured", return_value=(None, "auth_error")):
        recs = engine.generate_for_all_high_risk(db_conn, threshold=0.0, limit=2)
        assert len(recs) > 0
        for r in recs:
            assert r["generation_source"] == "offline_fallback"
            assert r["model_name"] == "deterministic_rule_engine"
            assert r["fallback_reason"] == "auth_error"

def test_timeout_triggers_error_fallback(db_conn):
    """
    Test 4: Verifies that network/request timeout falls back gracefully with fallback_reason='timeout'.
    """
    engine = RecommendationEngine(api_key="mock_key")
    with patch.object(engine.client, "generate_structured", return_value=(None, "timeout")):
        recs = engine.generate_for_all_high_risk(db_conn, threshold=0.0, limit=2)
        assert len(recs) > 0
        for r in recs:
            assert r["generation_source"] == "offline_fallback"
            assert r["model_name"] == "deterministic_rule_engine"
            assert r["fallback_reason"] == "timeout"

def test_quota_exceeded_triggers_error_fallback(db_conn):
    """
    Test 5: Verifies that 429 quota exhaustion falls back gracefully with fallback_reason='quota_exceeded'.
    """
    engine = RecommendationEngine(api_key="mock_key")
    with patch.object(engine.client, "generate_structured", return_value=(None, "quota_exceeded")):
        recs = engine.generate_for_all_high_risk(db_conn, threshold=0.0, limit=2)
        assert len(recs) > 0
        for r in recs:
            assert r["generation_source"] == "offline_fallback"
            assert r["model_name"] == "deterministic_rule_engine"
            assert r["fallback_reason"] == "quota_exceeded"

def test_malformed_json_or_schema_error_triggers_fallback(db_conn):
    """
    Test 6: Verifies that JSON decoding or schema validation failure falls back with fallback_reason='schema_validation_error'.
    """
    engine = RecommendationEngine(api_key="mock_key")
    with patch.object(engine.client, "generate_structured", return_value=(None, "schema_validation_error")):
        recs = engine.generate_for_all_high_risk(db_conn, threshold=0.0, limit=2)
        assert len(recs) > 0
        for r in recs:
            assert r["generation_source"] == "offline_fallback"
            assert r["model_name"] == "deterministic_rule_engine"
            assert r["fallback_reason"] == "schema_validation_error"

def test_hallucinated_instance_id_rejected(db_conn):
    """
    Test 7: Verifies anti-hallucination guard: any hallucinated instance ID returned by Gemini
    is rejected and does not pollute recommendations.
    """
    engine = RecommendationEngine(api_key="mock_key")
    target_instances = db_conn.execute("SELECT instance_id FROM risk_scores ORDER BY overall_risk_score DESC LIMIT 2").fetchall()
    real_inst_1 = target_instances[0][0]
    fake_inst = "i-hallucinated-fake-99999"

    mock_batch = GeminiRecommendationBatchResponse(
        recommendations=[
            GeminiRecommendationItem(
                instance_id=real_inst_1,
                priority="High",
                title="Valid Instance Recommendation",
                explanation="Valid explanation.",
                recommended_action="Valid action.",
                expected_benefit="Valid benefit.",
                source="gemini",
                model_name="gemini-3.8-flash",
                estimated_savings_usd=10.0,
                estimated_effort_hours=1.0
            ),
            GeminiRecommendationItem(
                instance_id=fake_inst,
                priority="Critical",
                title="Hallucinated Fake Instance",
                explanation="Invented by LLM hallucination.",
                recommended_action="Do nothing.",
                expected_benefit="None.",
                source="gemini",
                model_name="gemini-3.8-flash",
                estimated_savings_usd=0.0,
                estimated_effort_hours=1.0
            )
        ]
    )

    with patch.object(engine.client, "generate_structured", return_value=(mock_batch, None)):
        recs = engine.generate_for_all_high_risk(db_conn, threshold=0.0, limit=2)
        rec_ids = [r["instance_id"] for r in recs]
        assert fake_inst not in rec_ids
        assert real_inst_1 in rec_ids

def test_no_duplicate_recommendations_on_rerun(db_conn):
    """
    Test 8: Verifies idempotent persistence: re-running save_recommendations does not duplicate rows.
    """
    engine = RecommendationEngine(api_key="")
    recs = engine.generate_for_all_high_risk(db_conn, threshold=0.0, limit=3)
    assert len(recs) > 0

    conn = get_connection()
    try:
        engine.save_recommendations(conn, recs)
        count_1 = conn.execute("SELECT COUNT(*) FROM recommendations").fetchone()[0]

        # Re-save identical recommendation batch
        engine.save_recommendations(conn, recs)
        count_2 = conn.execute("SELECT COUNT(*) FROM recommendations").fetchone()[0]

        assert count_1 == count_2
        assert count_1 == len(recs)
    finally:
        conn.close()

def test_every_recommendation_links_to_valid_instance(db_conn):
    """
    Test 9: Asserts referential integrity: all linked instance IDs exist in cloud_instances.
    """
    df = db_conn.execute("""
        SELECT r.instance_id, ci.instance_id AS linked_id
        FROM recommendations r
        LEFT JOIN cloud_instances ci ON r.instance_id = ci.instance_id
    """).fetchdf()
    assert df["linked_id"].isnull().sum() == 0

def test_recommendations_priority_values_valid(db_conn):
    """
    Test 10: Asserts every row's priority belongs to the allowed domain [Critical, High, Medium, Low].
    """
    df = db_conn.execute("SELECT DISTINCT priority FROM recommendations").fetchdf()
    valid_priorities = {"Critical", "High", "Medium", "Low"}
    for p in df["priority"]:
        assert p in valid_priorities

def test_safe_logging_never_exposes_api_key():
    """
    Test 11: Asserts that API keys are redacted from logs and errors are classified cleanly.
    """
    secret = "secret-token-abcdef123456789"
    log_line = f"Connection failed with key {secret} and AIzaSyD9876543210987654321098765432101"
    sanitized = sanitize_text(log_line, secret)

    assert secret not in sanitized
    assert "AIzaSyD" not in sanitized
    assert "[REDACTED_API_KEY]" in sanitized

    # Check error classification handles various error shapes safely
    class MockAuthErr(Exception):
        code = 401
    assert classify_error(MockAuthErr("401 Unauthorized API key")) == "auth_error"

    class MockQuotaErr(Exception):
        code = 429
    assert classify_error(MockQuotaErr("RESOURCE_EXHAUSTED")) == "quota_exceeded"

def test_schema_migration_idempotent():
    """
    Test 12: Asserts running schema migration multiple times on existing DB succeeds idempotently.
    """
    conn = get_connection()
    try:
        migrate_schema(conn)
        migrate_schema(conn)

        columns = [col[1] for col in conn.execute("PRAGMA table_info('recommendations')").fetchall()]
        assert "generation_source" in columns
        assert "model_name" in columns
        assert "fallback_reason" in columns
        assert "expected_benefit" in columns
    finally:
        conn.close()

def test_insights_engine_deterministic_fallback(db_conn):
    """
    Test 13: Verifies InsightsEngine generates an executive summary deterministically when offline.
    """
    insights = InsightsEngine(api_key="")
    summary = insights.generate_executive_summary(db_conn)
    assert isinstance(summary, str)
    assert len(summary) > 20
    assert "Deterministic Fallback Summary" in summary or "instances" in summary.lower()

def test_executive_summary_printed_exactly_once(capsys):
    """
    Test 14 (Regression): Verifies standalone recommendation execution prints the executive summary
    exactly once without duplication.
    """
    run_recs_main()
    captured = capsys.readouterr().out

    # Header and summary banner checks
    assert captured.count("=== EXECUTIVE SUMMARY REPORT ===") == 1
    assert captured.count("[Deterministic Fallback Summary]") == 1

def test_application_controlled_provenance_overwrites_gemini_claims(db_conn):
    """
    Test 15: Verifies that application code strictly assigns provenance,
    overwriting any fabricated source or model claims declared in Gemini response payload.
    """
    engine = RecommendationEngine(api_key="mock_key", model_name="gemini-3.8-flash")
    target_instances = db_conn.execute("SELECT instance_id FROM risk_scores ORDER BY overall_risk_score DESC LIMIT 1").fetchall()
    inst_1 = target_instances[0][0]

    # Malicious/fabricated response from model claiming false provenance
    mock_batch = GeminiRecommendationBatchResponse(
        recommendations=[
            GeminiRecommendationItem(
                instance_id=inst_1,
                priority="High",
                title="Mock Test Instance Action",
                explanation="Observed metrics testing.",
                recommended_action="Apply security hardening steps.",
                expected_benefit="Risk score reduction.",
                source="offline_fallback",  # Model falsely claims offline_fallback
                model_name="fake-model-gpt4",  # Model falsely claims fake-model
                estimated_savings_usd=25.0,
                estimated_effort_hours=1.0
            )
        ]
    )

    with patch.object(engine.client, "generate_structured", return_value=(mock_batch, None)):
        recs = engine.generate_for_all_high_risk(db_conn, threshold=0.0, limit=1)
        assert len(recs) == 1
        rec = recs[0]

        # Authoritative application overwrite
        assert rec["generation_source"] == "gemini"
        assert rec["model_name"] == "gemini-3.8-flash"
        assert rec["fallback_reason"] is None
        assert rec["expected_benefit"] == "Risk score reduction."

        # Save to DB and verify stored record
        conn = get_connection()
        try:
            engine.save_recommendations(conn, recs)
            row = conn.execute("SELECT generation_source, model_name, fallback_reason, expected_benefit FROM recommendations WHERE instance_id = ?", (inst_1,)).fetchone()
            assert row[0] == "gemini"
            assert row[1] == "gemini-3.8-flash"
            assert row[2] is None
            assert row[3] == "Risk score reduction."
        finally:
            conn.close()

def test_legacy_schema_migration_preserves_honesty():
    """
    Test 16: Verifies that pre-Phase-3 recommendation records are honestly marked
    as 'legacy_unknown' and not falsely attributed to deterministic fallback or Gemini.
    """
    # Create isolated in-memory DuckDB database
    mem_conn = duckdb.connect(":memory:")
    try:
        # Pre-Phase-3 table schema (11 columns only, missing provenance & expected_benefit)
        mem_conn.execute("""
            CREATE TABLE recommendations (
                recommendation_id VARCHAR,
                instance_id VARCHAR,
                risk_type VARCHAR,
                priority VARCHAR,
                title VARCHAR,
                description VARCHAR,
                implementation_steps VARCHAR,
                estimated_savings_usd DOUBLE,
                estimated_effort_hours DOUBLE,
                status VARCHAR DEFAULT 'pending',
                generated_at TIMESTAMP
            )
        """)

        # Insert a pre-Phase-3 historical recommendation row
        mem_conn.execute("""
            INSERT INTO recommendations VALUES (
                'rec-legacy-001', 'i-legacy-001', 'cost', 'High', 'Old Title',
                'Old description without known provenance.', 'Step 1 | Step 2',
                50.0, 1.0, 'pending', '2026-01-01 00:00:00'
            )
        """)

        # Run migration 1st time
        migrate_schema(mem_conn)

        row = mem_conn.execute("SELECT generation_source, model_name, fallback_reason, expected_benefit FROM recommendations WHERE recommendation_id = 'rec-legacy-001'").fetchone()
        assert row[0] == "legacy_unknown"
        assert row[1] == "unknown"
        assert row[2] == "pre_migration_record"
        assert row[3] is None

        # Run migration 2nd time to prove idempotency
        migrate_schema(mem_conn)

        row_after = mem_conn.execute("SELECT generation_source, model_name, fallback_reason, expected_benefit FROM recommendations WHERE recommendation_id = 'rec-legacy-001'").fetchone()
        assert row_after[0] == "legacy_unknown"
        assert row_after[1] == "unknown"
        assert row_after[2] == "pre_migration_record"
        assert row_after[3] is None
    finally:
        mem_conn.close()

def test_expected_benefit_persisted_and_queried(db_conn):
    """
    Test 17: Verifies expected_benefit is saved into DuckDB and queryable via data_access.
    """
    from dashboard.utils.data_access import get_recommendations
    df = get_recommendations()
    assert "expected_benefit" in df.columns
    assert not df.empty
    # Seeded rows have non-null expected_benefit
    valid_benefits = df["expected_benefit"].dropna()
    assert len(valid_benefits) > 0
