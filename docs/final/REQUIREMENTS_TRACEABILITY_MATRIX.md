# CLARA Requirements Traceability Matrix (RTM)

**System:** CLARA: Cloud-Linked Evaluation and Risk Assessment using Predictive Analytics and Business Intelligence  
**Academic Course:** CSE 4191 – Minor Specialization Mini Project (Data Analytics)  
**Institution:** Manipal Institute of Technology Bengaluru  
**Academic Year:** 2026 – 2027  

---

## 1. System Requirements Traceability Matrix

| Req ID | Requirement Description | Implementation Module | DuckDB Entity / Schema | Verification Test Case | Technical Report Section |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-01** | Multi-Cloud Telemetry Generation: 300 instances across AWS, Azure, GCP over 90 days. | `data_generator/generator.py` | `cloud_instances`, `metrics_daily` | `tests/test_data_quality.py::test_instances_row_count` | Section 3.2, Table 3.1 |
| **REQ-02** | Ground-Truth Anomaly Injection: 15 scenarios across 5 distinct categories (`cpu_spike`, `brute_force`, `network_exfiltration`, `misconfiguration`, `memory_leak`). | `data_generator/generator.py` | `anomaly_manifest.json` | `tests/test_data_quality.py::test_anomaly_manifest_exists_and_has_15_entries` | Section 3.2, Table 4.2 |
| **REQ-03** | Embedded Columnar Warehousing: DuckDB schema, ACID operations, in-process OLAP. | `warehouse/db_connection.py`, `warehouse/schema.sql` | `clara.db` (6 tables) | `tests/test_models.py::test_risk_scores_table_populated` | Section 3.3, Figure 3.3 |
| **REQ-04** | 11 Engineered Rolling Time-Series Features: robust z-scores, rolling slopes, peak ratios. | `analytics/anomaly_model.py` | In-memory feature matrix | `tests/test_anomaly_model.py::test_telemetry_features_completeness` | Section 3.4, Table 3.2 |
| **REQ-05** | Isolation Forest Anomaly Detection: Reproducible model (seed 42), ≥80% Prec, ≥85% Rec. | `analytics/anomaly_model.py` | `risk_scores` | `tests/test_anomaly_model.py::test_evaluate_predictions_metrics` | Section 4.3, Table 4.1 |
| **REQ-06** | Manifest Isolation: Zero access to manifest labels during training or inference. | `analytics/anomaly_model.py` | Evaluator isolation | `tests/test_anomaly_model.py::test_no_manifest_ground_truth_leakage` | Section 4.2 |
| **REQ-07** | Deterministic Security Posture Scoring: Observable encryption, IAM, exposure, vulnerability indicators. | `analytics/security_model.py` | `security_configurations` | `tests/test_models.py::test_security_risk_model` | Section 3.5 |
| **REQ-08** | FinOps Rightsizing Engine: K-Means clustering (k=3), idle instance isolation, waste calc. | `analytics/cost_model.py` | `cost_data` | `tests/test_models.py::test_cost_waste_model` | Section 3.6, Table 4.3 |
| **REQ-09** | Composite Risk Scoring: Weighted `0.5*Sec + 0.3*Anom + 0.2*Waste`, bounded [0, 100]. | `analytics/run_all_models.py`, `dashboard` | `risk_scores`, `overall_risk_score` | `tests/test_dashboard.py::test_scoring_formula_parity_against_run_all_models` | Section 3.7, Figure 3.5 |
| **REQ-10** | Centralized Operational Risk Tiers: Critical, High, Medium, Low, and Unknown. | `dashboard/utils/data_access.py` | CASE SQL + Python Enum | `tests/test_dashboard.py::test_risk_tier_boundaries_critical` | Section 3.7, Table 3.3 |
| **REQ-11** | Modern Google GenAI SDK: Migration to `google-genai` SDK and `gemini-3.8-flash`. | `genai/gemini_client.py` | `recommendations` | `tests/test_recommendations.py::test_live_gemini_success` | Section 3.8 |
| **REQ-12** | Structured Pydantic Output Contracts: Non-negative savings, valid enums, instance check. | `genai/schemas.py` | Pydantic `RecommendationList` | `tests/test_recommendations.py::test_expected_benefit_persisted_and_queried` | Section 3.8, Appendix B |
| **REQ-13** | Anti-Hallucination Guard: Validates that returned instance IDs exist in candidates. | `genai/recommendation_engine.py` | DB candidate validation | `tests/test_recommendations.py::test_hallucinated_instance_id_rejected` | Section 3.8, Section 4.6 |
| **REQ-14** | Application-Controlled Provenance: App explicitly writes source, model, and fallback. | `genai/recommendation_engine.py` | `generation_source`, `model_name` | `tests/test_recommendations.py::test_application_controlled_provenance_overwrites_gemini_claims` | Section 3.8, Figure 3.6 |
| **REQ-15** | Deterministic Offline Fallback: The pipeline remains operational in tested missing-key and API-failure scenarios. | `genai/insights_engine.py` | `recommendations` | `tests/test_recommendations.py::test_missing_api_key_triggers_offline_fallback` | Section 3.8, Section 4.6 |
| **REQ-16** | 4-Page Streamlit BI Dashboard: Overview, Security, Cost, AI Recommendations. | `dashboard/app.py`, `dashboard/pages/` | Streamlit Multi-Page | `tests/test_dashboard.py::test_all_chart_components_render_figures` | Section 3.9 |
| **REQ-17** | Test Isolation Architecture: Temporary session directory fixtures (`tmp_path`). | `tests/conftest.py` | Session tmp DuckDB | `tests/test_anomaly_model.py::test_no_hardcoded_instances_seeds_or_labels` | Section 4.7, Figure 4.1 |
| **REQ-18** | Reproducible statement coverage across runtime application packages. | Full test suite plus explicit `.coveragerc` scope | Pytest-Cov report | `pytest --cov --cov-report=term-missing` (67% verified) | Section 4.7, Table 4.4 |
| **REQ-19** | Advisory Decision-Support Boundary: Zero autonomous cloud modification. | Architecture & UI runbooks | Read-only telemetry | Manual code audit & documentation | Section 1.5, Section 5.2 |
| **REQ-20** | Secret Protection: Zero exposed API keys in code, logs, or repositories. | `.env`, `.gitignore` | Environment variables | Repository secret scan | Section 5.3 |
