# CLARA: Cloud-Linked Evaluation and Risk Assessment

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Database DuckDB](https://img.shields.io/badge/database-DuckDB_1.1.3-amber.svg)](https://duckdb.org/)
[![Model Isolation Forest](https://img.shields.io/badge/ML-Isolation_Forest-purple.svg)](https://scikit-learn.org/)
[![GenAI Google GenAI SDK](https://img.shields.io/badge/GenAI-google--genai_gemini--3.8--flash-emerald.svg)](https://ai.google.dev/)
[![Tests Passing](https://img.shields.io/badge/tests-75%2F75_passing-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-67%25_statement-yellow.svg)](tests/)
[![Academic Project](https://img.shields.io/badge/MIT_Bengaluru-CSE_4191_Minor_Project-navy.svg)](reference_material/docs/)

> **Academic Submission:** B.Tech Minor Specialization Mini Project in Data Analytics (CSE 4191)  
> **Institution:** Department of Computer Science and Engineering, Manipal Institute of Technology Bengaluru  
> **Academic Year:** 2026 – 2027  
> **Student Team:** Johann Mathew Sajan (`235890104`), Nandan Murali (`235890114`), Abhijay Gupta (`235890206`), Arshia Gali (`235890070`)  
> **Project Guide:** Dr. Geetabai S Hukkeri, Assistant Professor, Dept. of CSE, MIT Bengaluru  
> **Minor Specialization Coordinator:** Dr. Rashmi R, Assistant Professor  

---

## 1. Executive Overview

**CLARA (Cloud-Linked Evaluation and Risk Assessment)** is an advisory decision-support platform designed for unified multi-cloud observability, multi-modal anomaly detection, explainable security risk scoring, FinOps cost rightsizing, and Generative AI operational recommendations.

Enterprise cloud deployments routinely span multiple Cloud Service Providers—primarily **Amazon Web Services (AWS)**, **Microsoft Azure**, and **Google Cloud Platform (GCP)**. While multi-cloud architectures provide operational redundancy, they create acute operational fragmentation:
- **Telemetry Silos:** Metrics are trapped in isolated monitoring consoles (AWS CloudWatch, Azure Monitor, GCP Cloud Operations).
- **Alert Fatigue:** Naive static thresholds generate hundreds of false alarms, burying insidious anomalies like slow memory leaks and brute-force activity.
- **Detached FinOps:** Cost management tools report billing overruns post-facto without correlating spend to idle or misconfigured infrastructure.
- **Ungrounded GenAI:** Generic chatbots hallucinate cloud resource IDs, lack structured schemas, and fail during external API downtime.

CLARA resolves this trilemma by unifying multi-cloud telemetry, explainable machine learning models, and modern Generative AI into an embedded analytical platform.

> [!IMPORTANT]
> **Advisory Decision-Support Boundary:**  
> CLARA is architected strictly as an **advisory decision-support platform**. In enterprise cloud environments, autonomous write actions (e.g. terminating running VMs or revoking IAM credentials) carry catastrophic outage risks. CLARA computes deterministic risk tiers, highlights anomalies, and generates prioritized, human-verifiable remediation playbooks, leaving final execution to human cloud engineers.

---

## 2. Key Architecture Pillars

```
+---------------------------------------------------------------------------------------------------+
|                                      CLARA 4-TIER ARCHITECTURE                                    |
+---------------------------------------------------------------------------------------------------+
|  1. INGESTION LAYER                                                                               |
|     • 300 Multi-Cloud Instances (AWS 155 / Azure 88 / GCP 57 in the active database)              |
|     • 90-Day Telemetry Window (27,000 metrics records with diurnal patterns & noise)              |
|     • 15 Injected Anomaly Scenarios (cpu_spike, brute_force, network_exfil, misconfig, memory_leak)|
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|  2. EMBEDDED ANALYTICAL WAREHOUSE (DuckDB: clara.db)                                              |
|     • In-Process Columnar Storage (27k rows ingested in-process, zero server daemons)             |
|     • Normalized Tables: cloud_instances, metrics_daily, cost_data, security_configurations,      |
|                          risk_scores, security_events, recommendations                            |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|  3. ANALYTICS & RISK SCORING ENGINES                                                              |
|     • Multi-Modal Anomaly Detector: Isolation Forest + 11 engineered rolling time-series features |
|       (Precision: 82.35%, Recall: 93.33%, F1: 0.8750 on isolated ground-truth corpus)             |
|     • FinOps Rightsizing: K-Means clustering (k=3), $184.58 cost savings; $220.87 total savings   |
|     • Security Posture Scorer: Deterministic scoring on observable encryption, IAM, exposure,     |
|       vulnerability-age and security-event indicators (0-100)                                     |
|     • Composite Risk: 0.50*Security + 0.30*Anomaly + 0.20*CostWaste (Tiers: Critical, High, Low) |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|  4. PRESENTATION & DECISION SUPPORT LAYER                                                         |
|     • Dual-Engine GenAI Advisory: Google GenAI SDK (gemini-3.8-flash) with Pydantic validation    |
|       + Deterministic Offline Rule Fallback Engine (application-controlled provenance)            |
|     • Interactive Streamlit Dashboard: 4 BI pages (Overview, Security, Cost, AI Recommendations)  |
+---------------------------------------------------------------------------------------------------+
```

---

## 3. Verified Performance & Acceptance Metrics

| Metric / Dimension | Stated Acceptance Criteria | CLARA Production Result | Verification Status |
| :--- | :--- | :--- | :---: |
| **Anomaly Precision** | $\ge 80.0\%$ | **82.35%** (14 TP / 17 Positives) | **PASSED** |
| **Anomaly Recall** | $\ge 85.0\%$ | **93.33%** (14 TP / 15 Injected Anomalies) | **PASSED** |
| **Anomaly F1-Score** | N/A | **0.8750** | **OPTIMAL** |
| **Category Detection Breadth** | All 5 categories with ≥1 hit | **5 / 5 categories detected (100%)** | **PASSED** |
| **Honest Recall Breakdown** | Transparent per-type reporting | `brute_force`: 3/3 (100%), `cpu_spike`: 3/3 (100%), `network_exfil`: 3/3 (100%), `misconfig`: 3/3 (100%), `memory_leak`: 2/3 (66.7%) | **VERIFIED** |
| **Manifest Isolation** | Zero access to manifest labels | Manifest held out during training & inference | **PASSED** |
| **Recommendation Savings** | Quantified monthly opportunity | **$184.58/month cost-only; $220.87/month across all recommendation types** | **VERIFIED** |
| **GenAI SDK & Endpoint**| Modern SDK (not deprecated) | `google-genai==2.34.0`, `gemini-3.8-flash` | **VERIFIED** |
| **Schema Validation** | 100% Pydantic conformance | 10/10 Live Gemini recommendations validated | **VERIFIED** |
| **Test Suite Pass Rate**| 100% Passing Tests | **75 / 75 Tests Passed** | **PASSED** |
| **Statement Coverage** | Honest runtime-package measurement | **67% statement coverage** | **VERIFIED** |
| **Test Isolation** | Zero mutation to `clara.db` | Hash unchanged: `DE271EA91DA0DF...` | **PASSED** |

---

## 4. Quick Start (Windows PowerShell)

### Step 1: Activate Environment & Install Dependencies
```powershell
cd "path\to\CLARA-Minor-Specialization-Project"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

To install documentation generation dependencies:
```powershell
pip install -r requirements-docs.txt
```

### Step 2: (Optional) Configure Gemini API Key
CLARA runs seamlessly offline using its deterministic rule engine. To enable live Gemini recommendations, configure your API key in `.env`:
```powershell
# Create .env file
Set-Content -Path .env -Value "GEMINI_API_KEY=your_actual_gemini_api_key_here"
```

### Step 3: Launch the Interactive Dashboard
```powershell
streamlit run dashboard/app.py
```
*Open your web browser at `http://localhost:8501` to explore the 4-page BI interface.*

### Step 4: Run the Automated Test Suite & Coverage
```powershell
# Run all 75 tests
pytest -v

# Run with statement coverage report
pytest --cov --cov-report=term-missing
```

### Step 5: Run the Anomaly Precision & Recall Evaluator
```powershell
python -m analytics.evaluate_anomaly_model
```

---

## 5. Pipeline Stages & Execution Commands

| Stage | Script / Command | Description |
| :--- | :--- | :--- |
| **Stage 1: Warehouse Verification** | `python -c "import duckdb; print(duckdb.connect('clara.db', read_only=True).execute('SHOW TABLES').fetchall())"` | Verifies tables in `clara.db` without modifying it. |
| **Stage 2: Analytics Training** | `python -m analytics.run_all_models` | Re-trains Isolation Forest, fits K-Means rightsizing, and calculates posture scores. |
| **Stage 3: Recommendation Orchestrator** | `python -m genai.run_recommendations` | Triages candidates and runs `gemini-3.8-flash` (or deterministic offline fallback). |
| **Stage 4: Anomaly Model Evaluation** | `python -m analytics.evaluate_anomaly_model` | Evaluates detector performance against isolated `anomaly_manifest.json`. |
| **Stage 5: BI Dashboard** | `streamlit run dashboard/app.py` | Launches multi-page Streamlit interface with reactive filters and provenance badges. |
| **Stage 6: Test Suite & Coverage** | `pytest --cov --cov-report=term-missing` | Executes the isolated test suite with explicit runtime-package coverage. |

---

## 6. Repository Layout

```
CLARA-Final-Project/
├── .env.example                     # Template for environment configuration (placeholders only)
├── .gitignore                       # Git ignore rules (protects .env, .venv, caches)
├── requirements.txt                 # Runtime and test dependencies
├── requirements-docs.txt            # Documentation generation dependencies
├── pytest.ini                       # Pytest configuration
├── README.md                        # Root technical documentation
├── clara.db                         # DuckDB production database (SHA256 verified)
├── clara.db.live_backup             # Backup of production database
│
├── data/                            # Raw datasets & generation
│   ├── generate_synthetic_data.py   # Multi-cloud generator
│   └── synthetic/                   # Generated CSVs & isolated anomaly_manifest.json
│
├── warehouse/                       # Embedded analytical warehouse
│   ├── db_connection.py             # Database connection utilities
│   ├── load_data.py                 # Bulk loading utilities
│   └── schema.sql                   # Relational DDL schema
│
├── analytics/                       # Machine learning & scoring engines
│   ├── anomaly_model.py             # Isolation Forest model & 11 time-series features
│   ├── cost_model.py                # K-Means rightsizing & waste calculator
│   ├── security_model.py            # Deterministic posture scoring engine
│   ├── run_all_models.py            # Orchestrator computing composite risk scores
│   └── evaluate_anomaly_model.py    # Independent evaluation against ground truth
│
├── genai/                           # Recommendation systems
│   ├── gemini_client.py             # Modern Google GenAI SDK (gemini-3.8-flash)
│   ├── schemas.py                   # Pydantic structured output contracts
│   ├── recommendation_engine.py     # Anti-hallucination guard & provenance stamping
│   ├── insights_engine.py           # Deterministic offline heuristic rule engine
│   └── run_recommendations.py       # Recommendation orchestrator CLI
│
├── dashboard/                       # Multi-page Streamlit BI application
│   ├── app.py                       # Application entry point
│   ├── pages/
│   │   ├── 1_Overview.py            # Fleet KPIs ($184.58 cost-only / $220.87 all recommendation savings)
│   │   ├── 2_Security_Analysis.py   # Forensic vulnerability & exposure breakdown
│   │   ├── 3_Cost_Analysis.py       # FinOps rightsizing scatter plots & waste table
│   │   └── 4_Recommendations.py     # AI cards with Gemini vs Offline provenance badges
│   ├── components/charts.py         # Visual chart components
│   └── utils/
│       ├── data_access.py           # Database query functions & aggregations
│       └── risk_tiers.py            # Centralized risk tiers (Critical, High, Unknown)
│
├── tests/                           # Automated tests and release-readiness checks (67% runtime-package coverage)
│   ├── conftest.py                  # Session-scoped temporary database isolation harness
│   ├── test_anomaly_model.py        # 11 rolling features & Isolation Forest tests
│   ├── test_dashboard.py            # Risk tier consistency & formula parity tests
│   ├── test_data_quality.py         # Synthetic generator schema & reproducibility tests
│   ├── test_models.py               # ML model integration tests
│   └── test_recommendations.py      # Pydantic validation & offline fallback tests
│
└── docs/final/                      # Academic documentation & submission deliverables
    ├── CLARA_Final_Project_Report.docx  # Academic technical report (Word)
    ├── CLARA_Final_Project_Report.pdf   # Academic technical report (PDF)
    ├── CLARA_Final_Presentation.pptx    # University presentation deck (PowerPoint)
    ├── CLARA_Final_Presentation.pdf     # University presentation deck (PDF)
    ├── CLARA_Presentation_Script.docx   # Spoken defense narration (Word)
    ├── CLARA_Presentation_Script.md     # Spoken defense narration (Markdown)
    ├── CLARA_Project_Diary.docx         # Student project diary (Word)
    ├── CLARA_Project_Diary.pdf          # Student project diary (PDF)
    ├── DEMO_GUIDE.md                    # Demonstration walkthrough
    ├── INSTALLATION_GUIDE.md            # Operator & setup manual
    ├── PROJECT_OVERVIEW.md              # Executive technical summary
    ├── VIVA_QUESTIONS_AND_ANSWERS.md    # 40+ technical questions & answers for viva
    ├── REQUIREMENTS_TRACEABILITY_MATRIX.md # Traceability mapping matrix
    ├── figures/                         # 7 publication-grade 300 DPI architecture diagrams
    └── screenshots/                     # Manual capture checklist & instructions
```

---

## 7. Academic Verification & Documentation Deliverables

All academic documents are formatted strictly according to the official guidelines of Manipal Institute of Technology Bengaluru:
- **Final Technical Report:** Available in [`docs/final/CLARA_Final_Project_Report.docx`](docs/final/CLARA_Final_Project_Report.docx) and [`docs/final/CLARA_Final_Project_Report.pdf`](docs/final/CLARA_Final_Project_Report.pdf).
- **Presentation Deck:** Available in [`docs/final/CLARA_Final_Presentation.pptx`](docs/final/CLARA_Final_Presentation.pptx) and [`docs/final/CLARA_Final_Presentation.pdf`](docs/final/CLARA_Final_Presentation.pdf).
- **Spoken Defense Script:** Available in [`docs/final/CLARA_Presentation_Script.docx`](docs/final/CLARA_Presentation_Script.docx) and [`docs/final/CLARA_Presentation_Script.md`](docs/final/CLARA_Presentation_Script.md).
- **Student Mini-Project Diary:** Available in [`docs/final/CLARA_Project_Diary.docx`](docs/final/CLARA_Project_Diary.docx) and [`docs/final/CLARA_Project_Diary.pdf`](docs/final/CLARA_Project_Diary.pdf).
- **Demonstration Guide:** [`docs/final/DEMO_GUIDE.md`](docs/final/DEMO_GUIDE.md).
- **Viva Preparation Guide:** [`docs/final/VIVA_QUESTIONS_AND_ANSWERS.md`](docs/final/VIVA_QUESTIONS_AND_ANSWERS.md).

---

## 8. License & Academic Integrity

This project was developed as an authentic academic minor specialization project at the Department of Computer Science and Engineering, Manipal Institute of Technology Bengaluru. All machine learning evaluations, data warehousing architectures, and Generative AI schemas were independently constructed, rigorously tested, and verified under faculty supervision.
