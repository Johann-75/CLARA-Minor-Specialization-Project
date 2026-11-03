# CLARA Demonstration Screenshots Guide & Manual Capture Checklist

**Status:** PENDING MANUAL CAPTURE  
*(Screenshots must be captured manually from the running Streamlit dashboard and terminal before final presentation defense.)*

---

## 1. Required Screenshot Inventory & Exact Placeholders

The following 8 screenshots must be captured and placed in this directory (`docs/final/screenshots/`):

| File Name | Page / View | Visual Focus & Elements to Capture | Status |
| :--- | :--- | :--- | :---: |
| `01_welcome.png` | `dashboard/app.py` | Welcome banner, platform description, 4-tier overview, sidebar navigation. | PENDING MANUAL ACTION |
| `02_executive_overview.png` | `1_Overview.py` | Top KPI cards ($184.58 cost-recommendation savings, $220.87 all-recommendation savings, 1 critical, 6 high), provider filter, risk distribution chart. | PENDING MANUAL ACTION |
| `03_security_analysis.png` | `2_Security_Analysis.py` | Security risk distribution chart, observable vulnerability indicators, open ports (22, 3389), IAM permissions. | PENDING MANUAL ACTION |
| `04_cost_optimization.png` | `3_Cost_Analysis.py` | FinOps rightsizing scatter plot (Cluster 0 vs 1 vs 2), spend vs waste trends, candidate downsizing table. | PENDING MANUAL ACTION |
| `05_live_gemini_recommendations.png` | `4_Recommendations.py` | Recommendation cards displaying green **`gemini (gemini-3.8-flash)`** and amber **`offline_fallback`** badges. | PENDING MANUAL ACTION |
| `06_expanded_recommendation.png` | `4_Recommendations.py` | Expanded recommendation card showing technical justification, savings ($), and step-by-step CLI remediation steps. | PENDING MANUAL ACTION |
| `07_test_results.png` | PowerShell Terminal | Terminal output of `pytest --cov --cov-report=term-missing` showing the full passing suite and **67% runtime-package coverage**. | PENDING MANUAL ACTION |
| `08_anomaly_evaluation.png` | PowerShell Terminal | Terminal output of `python -m analytics.evaluate_anomaly_model` showing **Precision: 82.35%**, **Recall: 93.33%**, F1: 0.8750. | PENDING MANUAL ACTION |

---

## 2. Screenshot Capture Instructions

### Step 1: Launch Streamlit Dashboard
```powershell
cd "path\to\CLARA-Minor-Specialization-Project"
.\.venv\Scripts\Activate.ps1
streamlit run dashboard/app.py
```
Open your browser at `http://localhost:8501`. Use standard 100% zoom at 1920x1080 resolution.

1. Capture `01_welcome.png` on the Home page.
2. Navigate to `1_Overview.py`, set provider filter to "AWS" or "All", capture `02_executive_overview.png`.
3. Navigate to `2_Security_Analysis.py`, capture `03_security_analysis.png`.
4. Navigate to `3_Cost_Analysis.py`, capture `04_cost_optimization.png`.
5. Navigate to `4_Recommendations.py`, capture `05_live_gemini_recommendations.png`.
6. Expand one recommendation card, capture `06_expanded_recommendation.png`.

### Step 2: Capture Terminal Outputs
In your PowerShell terminal:
```powershell
pytest --cov=. --cov-report=term
```
Capture the resulting summary block as `07_test_results.png`.

Then execute:
```powershell
python -m analytics.evaluate_anomaly_model
```
Capture the confusion matrix and recall table as `08_anomaly_evaluation.png`.
