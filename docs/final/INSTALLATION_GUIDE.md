# CLARA Installation & Operator Manual

**System:** CLARA: Cloud-Linked Evaluation and Risk Assessment using Predictive Analytics and Business Intelligence  
**Target Environment:** Windows 10 / Windows 11 (PowerShell)  
**Supported Runtime:** Python 3.11.x (64-bit)  
**Database:** Embedded DuckDB 1.1.x  

---

## 1. System Prerequisites

Before installing CLARA, ensure the following tools are available on your workstation:

1. **Python 3.11 (64-bit):**
   - Download from [python.org](https://www.python.org/downloads/) or install via Windows Terminal: `winget install Python.Python.3.11`
   - Verify installation:
     ```powershell
     python --version
     # Output must show Python 3.11.x
     ```
2. **PowerShell 5.1+ or PowerShell 7+**

---

## 2. Directory Setup & Virtual Environment

Navigate to the project root directory:

```powershell
cd "path\to\CLARA-Minor-Specialization-Project"
```

Create a dedicated virtual environment named `.venv`:

```powershell
python -m venv .venv
```

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

*Note: If PowerShell displays an execution policy error (`Execution_Policies`), enable local script execution for the current session:*
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\.venv\Scripts\Activate.ps1
```

---

## 3. Dependency Installation & Compatibility Constraints

### 3.1 Production & Test Dependencies
Upgrade `pip` and install all required runtime and test packages:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Verify critical installed packages:
```powershell
python -c "import duckdb, sklearn, streamlit, pydantic, google.genai, pyarrow; print('All core runtime libraries verified!')"
```

### 3.2 PyArrow & NumPy Compatibility Architecture
Streamlit's internal dataframe rendering relies on Apache Arrow via `pyarrow`. Unconstrained installations often pull PyArrow 17.0+ or newer, which causes runtime breakage:
```text
ImportError: pyarrow requires NumPy 2.0 or newer, found 1.26.4
```
Because CLARA's analytics and ML models (scikit-learn 1.5.0, pandas 2.2.2, DuckDB 1.0.0, and Isolation Forest) are calibrated on `numpy==1.26.4`, `requirements.txt` strictly pins:
```text
numpy==1.26.4
pyarrow==16.1.0
```
This guarantees 100% stable execution and enables all `st.dataframe` tables across the **Executive Overview**, **Security Analysis**, and **Cost Analysis** pages to render cleanly without native library crashes.

### 3.3 Documentation Generation Dependencies (Optional)
To regenerate project reports, presentations, and diaries:
```powershell
pip install -r requirements-docs.txt
```

---

## 4. Environment Variables Configuration (`.env`)

CLARA supports both online operation (using Google Gemini) and offline operation (using the deterministic rule fallback engine).

To enable live Google Gemini recommendations, create a `.env` file in the project root:

```powershell
# Create .env file
New-Item -ItemType File -Path .env -Force
```

Add your Gemini API key to `.env`:
```text
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### Security Best Practices:
- Never commit `.env` to Git version control. `.env` is explicitly included in `.gitignore`.
- If no `.env` file or `GEMINI_API_KEY` is present, the pipeline remains operational in the tested missing-key and API-failure scenarios by using a clearly labelled deterministic fallback.

---

## 5. Warehouse Verification & Pipeline Execution

### Step 5.1: Database Health Check
The project repository includes the fully pre-seeded, verified production database `clara.db` containing 300 instances, 27,000 metrics records, and 10 live Gemini recommendations.

Verify database integrity and record counts:
```powershell
python -c "import duckdb; con=duckdb.connect('clara.db', read_only=True); [print(f'{r[0]}: {con.execute(f\"select count(*) from {r[0]}\").fetchone()[0]} rows') for r in con.execute('show tables').fetchall()]; con.close()"
```

### Step 5.2: (Optional) Re-Running Analytics Models
To re-train the Isolation Forest anomaly detector, re-compute K-Means rightsizing clusters, and re-calculate posture scores:
```powershell
python -m analytics.run_all_models
```

### Step 5.3: (Optional) Re-Running Recommendation Generation
To execute the recommendation orchestrator:
```powershell
python -m genai.run_recommendations
```
- If `GEMINI_API_KEY` is present: Dispatches candidates to `gemini-3.8-flash`, validates Pydantic schema, verifies instance IDs, and stores records with `generation_source='gemini'`.
- If `GEMINI_API_KEY` is absent: Generates fallback recommendations with `generation_source='offline_fallback'`.

---

## 6. Launching the Interactive BI Dashboard

To launch the multi-page Streamlit application:

```powershell
streamlit run dashboard/app.py
```

The application will launch your default web browser at:
```text
http://localhost:8501
```

All 5 analytical views (Welcome, Executive Overview, Security Analysis, Cost Analysis, Recommendations) are fully accessible with responsive filters.

---

## 7. Automated Test Suite Execution & Coverage

CLARA features strict **test isolation**: running pytest executes inside session-scoped temporary directories (`tmp_path`), guaranteeing that your production `clara.db` database and synthetic CSVs remain bit-for-bit unchanged.

### Run All 82 Tests:
```powershell
pytest -v
```
Expected result: **75 passed**.

### Run Coverage Verification:
```powershell
pytest --cov --cov-report=term-missing
```
Expected result: **67% statement coverage across all configured runtime application packages**.

### Run Anomaly Detection Precision/Recall Evaluator:
```powershell
python -m analytics.evaluate_anomaly_model
```
Expected result:
- **Precision: 82.35%** (>= 80.0% requirement)
- **Recall: 93.33%** (>= 85.0% requirement)
- **F1-Score: 0.8750**
- **Category detection breadth: all 5 anomaly categories had at least one detected instance**
  - `brute_force`: 3/3 (100.0%)
  - `cpu_spike`: 3/3 (100.0%)
  - `memory_leak`: 2/3 (66.7%)
  - `misconfiguration`: 3/3 (100.0%)
  - `network_exfiltration`: 3/3 (100.0%)
