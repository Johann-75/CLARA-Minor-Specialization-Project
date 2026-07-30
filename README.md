# CLARA: Cloud-Linked Evaluation and Risk Assessment

CLARA (Cloud-Linked Evaluation and Risk Assessment) is a generative AI-powered cloud security and cost intelligence platform designed to detect, prioritize, and remediate cloud infrastructure risks while optimizing financial efficiency. By combining a multi-dimensional cloud analytics data warehouse with three specialized machine learning modules (anomaly detection, security scoring, cost waste prediction) and a Gemini API Natural Language Generation layer, CLARA translates complex technical risk metrics into actionable, business-readable recommendations presented through an interactive Streamlit dashboard.

## Quick Start (Full Pipeline)

To run the entire CLARA pipeline end-to-end (generation, database ingestion, ML model training, and AI recommendations generation) in one command:

1.  **Initialize Virtual Environment:**
    ```bash
    python -m venv venv && source venv/bin/activate
    ```
    *(On Windows PowerShell, use `venv\Scripts\Activate.ps1`)*

2.  **Install Required Packages:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Setup Environment Variables:**
    ```bash
    cp .env.example .env
    ```
    Edit the newly created `.env` file and append your `GEMINI_API_KEY`.

4.  **Run End-to-End Orchestrated Pipeline:**
    ```bash
    python run_pipeline.py
    ```

5.  **Launch the Interactive Dashboard:**
    ```bash
    streamlit run dashboard/app.py
    ```

### Re-running from scratch

If you want to fully reset the pipeline and re-run all calculations from a blank state, simply run:
```bash
# Delete the local DuckDB database file
rm clara.db

# Delete the previously generated synthetic CSVs
rm -r data/synthetic/

# Re-run pipeline from scratch
python run_pipeline.py
```

## Folder Structure

*   `data/`: Stores raw input datasets, intermediate tables, and generated synthetic/exported CSV data.
*   `warehouse/`: Contains the database connection configuration, SQL DDL schema files, and migrations.
*   `etl/`: Contains ETL pipelines responsible for extracting, transforming, and loading raw metrics into the normalized warehouse.
*   `analytics/`: Implements the machine learning modules for anomaly detection, security scoring, and cost prediction.
*   `genai/`: Wraps the Gemini API integration for generating natural language recommendations and executive insights.
*   `dashboard/`: Implements the interactive 4-page Streamlit dashboard and its visualization components.
*   `tests/`: House the automated test suite verifying data quality, model predictions, and dashboard views.
*   `data_generator/`: Contains scripts for generating the 90-day synthetic cloud infrastructure metric corpus.

## Setup Instructions

1.  **Create a Virtual Environment:**
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment Variables:**
    Copy the example environment file and fill in your Gemini API credentials:
    ```bash
    cp .env.example .env
    ```
    Then edit `.env` and set `GEMINI_API_KEY=your_actual_gemini_key_here`.

## Running the Project Stages

1.  **Stage 1: Generate Synthetic Data**
    Run the generator to create raw telemetry and configuration data:
    ```bash
    python -m data_generator.generator
    ```

2.  **Stage 2: Run ETL Pipeline**
    Process and load the generated data into the database warehouse:
    ```bash
    python -m etl.extract
    python -m etl.transform
    python -m etl.load
    ```

3.  **Stage 3: Run Analytics Risk Scoring**
    Train models and generate the combined risk scores:
    ```bash
    python -m analytics.anomaly_model
    python -m analytics.security_model
    python -m analytics.cost_model
    ```

4.  **Stage 4: Generate Recommendations**
    Send high-risk findings to Gemini to generate remediation steps:
    ```bash
    python -m genai.recommendation_engine
    ```

5.  **Stage 5: Launch the Streamlit Dashboard**
    Start the Business Intelligence interface:
    ```bash
    streamlit run dashboard/app.py
    ```

6.  **Run Automated Tests**
    Run the test suite to verify pipeline and model integrity:
    ```bash
    pytest
    ```
