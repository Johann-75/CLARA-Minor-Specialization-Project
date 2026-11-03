# CLARA Demonstration Walkthrough & Viva Guide

**Project:** CLARA: Cloud-Linked Evaluation and Risk Assessment using Predictive Analytics and Business Intelligence  
**Course Code:** CSE 4191 – Minor Specialization Mini Project (Data Analytics)  
**Institution:** Manipal Institute of Technology Bengaluru  
**Duration:** 5–7 Minutes Live Demonstration Workflow  

---

## 1. Executive Summary of Demonstration

This guide outlines a crisp, professional 5–7 minute live demonstration workflow designed for university project evaluators and viva examination panels. It showcases:
1. In-process analytical query execution using **DuckDB**;
2. Multi-modal **Isolation Forest** anomaly detection with 11 engineered time-series features (precision 82.35%, recall 93.33%, F1 0.8750);
3. Unsupervised **FinOps rightsizing** supporting **$184.58/month** in cost recommendations, with **$220.87/month** total savings across all recommendation types;
4. Explainable **Security Posture** scoring (0–100) based on observable encryption, IAM, exposure, vulnerability-age and security-event indicators;
5. Unified **Composite Risk** scoring and centralized severity tiers (Critical, High, Medium, Low, Unknown);
6. Modern **Google GenAI SDK (gemini-3.8-flash)** recommendations with strict **Pydantic validation**, anti-hallucination guards, and immutable application-controlled provenance;
7. Seamless **Deterministic Offline Fallback** operation;
8. Automated test suite execution with **all tests passing, 67% runtime-package coverage**, and **strict test isolation**.

---

## 2. Pre-Demo Environment Checklist

Before commencing the presentation, open two Windows PowerShell terminal windows:

### Terminal 1: Application Directory
```powershell
cd "path\to\CLARA-Minor-Specialization-Project"
.\.venv\Scripts\Activate.ps1
```

### Terminal 2: Test & Evaluation Terminal
```powershell
cd "path\to\CLARA-Minor-Specialization-Project"
.\.venv\Scripts\Activate.ps1
```

Verify that `clara.db` is intact (SHA256: `DE271EA91DA0DF6C2A22C9D967684574FBD3F63FE25B6CAB8A5C07C7B91F6BD8`):
```powershell
Get-FileHash clara.db -Algorithm SHA256
```

---

## 3. Minute-by-Minute Demonstration Flow

### Minute 0:00 – 1:00: Launch & Executive Overview (Page 1)
1. **Open the hosted Streamlit application:**
   Use the verified `*.streamlit.app` URL from `SUBMISSION_HANDOFF.md`. Keep the local command below only as a backup if campus internet is unavailable.

2. **Local backup command:**
   ```powershell
   streamlit run dashboard/app.py
   ```
   *The browser opens automatically at `http://localhost:8501`.*

3. **Highlight the Executive KPI Metric Cards:**
   - **Cost Recommendation Savings:** `$184.58/month`.
   - **All Recommendation Savings:** `$220.87/month` across cost, anomaly, and security recommendations.
   - **Anomaly Evaluation:** `15 injected` scenarios and `17 predicted` anomalous instances at the operational threshold.
   - **Critical / High Risk Instances:** `1` Critical instance (score ≥ 80.0), `6` High risk instances (60–80).

4. **Demonstrate Reactive Filtering:**
   - In the sidebar, select **Cloud Provider = AWS**. Point out how KPI cards and charts reactively re-aggregate in-process using DuckDB SQL pushdown.
   - Reset the filter to **All Providers**.

5. **Demonstrate Centralized Risk Tiers:**
   - Show the **Overall Risk Tier Breakdown**: Critical (red), High (orange), Medium (yellow), Low (green), and Unknown (neutral slate gray).
   - Point out that missing or invalid data is never silently clamped into Low.

---

### Minute 1:00 – 2:30: Security Forensics (Page 2)
1. **Navigate to `2_Security_Analysis` via the sidebar navigation.**
2. **Point out Key Security Visualizations:**
   - **Threat Breakdown:** Observable exposure across open administrative ports (SSH 22, RDP 3389) and administrative IAM permission levels.
   - **Vulnerability Profiling:** Unpatched vulnerability indicators.
   - Emphasize to evaluators: *Security scoring is deterministic and explainable, derived directly from observable encryption, IAM, exposure, vulnerability-age and security-event indicators rather than opaque black-box models.*

---

### Minute 2:30 – 3:45: FinOps Rightsizing & Cost Optimization (Page 3)
1. **Navigate to `3_Cost_Analysis`.**
2. **Explain K-Means Clustering Results:**
   - Point out the 3 operational clusters:
     - **Cluster 0 (Over-Provisioned / Idle):** Low average CPU and RAM utilization.
     - **Cluster 1 (Balanced Workloads):** Workloads operating in healthy 40–70% utilization range.
     - **Cluster 2 (Constrained / High Load):** Instances operating at high utilization (>84%).
3. **Show Cost and Overall Recommendation Savings:**
   - Point out **$184.58/month** from cost and rightsizing recommendations.
   - Explain that **$220.87/month** is the total across all recommendation types, not a cost-only value.
   - Emphasize that rightsizing recommendations downsize specific virtual machine families without impacting SLA requirements.

---

### Minute 3:45 – 5:00: Dual-Engine Recommendations & AI Provenance (Page 4)
1. **Navigate to `4_Recommendations`.**
2. **Demonstrate Provenance Badging:**
   - Point out the **Verified Live Gemini Recommendations** stored in DuckDB.
   - Note the distinct badge: **`Gemini (gemini-3.8-flash)`** in emerald green versus **`Deterministic Fallback`** in amber orange.
   - Emphasize that **provenance is application-controlled**: the Gemini API is never trusted to declare its own source.
3. **Inspect Recommendation Details:**
   - Expand a recommendation card.
   - Show:
     - **Action Title:** Short headline.
     - **Technical Justification:** Clear operational rationale derived from 90-day telemetry.
     - **Estimated Monthly Savings:** Quantified financial impact.
     - **Step-by-Step Remediation:** Clear CLI / Terraform steps for human cloud engineers.
4. **Highlight the Advisory Boundary:**
   - Explicitly remind evaluators: *CLARA is an advisory decision-support system. It generates reviewable playbooks for human operators and intentionally avoids risky autonomous write actions.*

---

### Minute 5:00 – 6:15: Offline Evaluator & Test Suite Verification
1. **Switch to Terminal 2 (Command Line).**
2. **Run the Offline Anomaly Evaluator:**
   ```powershell
   python -m analytics.evaluate_anomaly_model
   ```
   **Point out to Evaluators:**
   - **Precision: 82.35%** (exceeds ≥ 80.0% requirement);
   - **Recall: 93.33%** (14/15 detected, exceeds ≥ 85.0% requirement);
   - **F1-Score: 0.8750**;
   - **Category detection breadth: all 5 anomaly categories had at least one detected instance:**
     - `brute_force`: 3/3 (100.0%)
     - `cpu_spike`: 3/3 (100.0%)
     - `memory_leak`: 2/3 (66.7%)
     - `misconfiguration`: 3/3 (100.0%)
     - `network_exfiltration`: 3/3 (100.0%)
   - **Manifest Isolation:** The evaluation manifest was completely held out during feature engineering and training.

3. **Run the Full Test Suite with Statement Coverage:**
   ```powershell
   pytest --cov --cov-report=term-missing
   ```
   **Point out to Evaluators:**
   - **All tests passed**;
   - **67% statement coverage across all runtime application packages**;
   - **Zero Database Mutation:** Point out that all tests executed in session-scoped temporary directories (`tmp_path`), leaving production `clara.db` completely untouched and bit-for-bit identical.

---

### Minute 6:15 – 7:00: Concluding Summary & Examiner Q&A
1. Return to the browser Overview page.
2. Summarize key deliverables:
   - 300 multi-cloud instances in the active database (AWS 155 / Azure 88 / GCP 57);
   - In-process DuckDB columnar warehousing;
   - 11-feature Isolation Forest with 93.3% recall and 82.4% precision;
   - $184.58 monthly cost-recommendation savings and $220.87 total recommendation savings;
   - Dual-engine Gemini 3.8 Flash + deterministic offline rule fallback;
   - full test suite passing with 67% runtime-package coverage.
3. Open the floor for examiner questions.
