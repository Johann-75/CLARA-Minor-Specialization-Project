# CLARA Submission-Ready Design

## Intent

Prepare CLARA for a reliable university demonstration where evaluators can open a hosted Streamlit URL, inspect the four dashboard pages, and see results that agree with the submitted presentation, documentation, tests, and active `clara.db` database.

## Goals

- Make the local handoff the authoritative implementation and synchronize it to GitHub on a `submission-ready` branch.
- Preserve the verified `clara.db` content and SHA-256 hash.
- Make every visible metric unambiguous and consistent with the active database.
- Keep the dashboard functional without a Gemini API key by using the stored recommendations and deterministic fallback behavior.
- Make deployment to Streamlit Community Cloud reproducible from the repository.
- Verify the application with the full test suite, anomaly evaluator, database audit, and Streamlit page tests.
- Merge into `main` only after verification, then deploy and provide a short presentation runbook.

## Non-Goals

- Do not regenerate the synthetic dataset.
- Do not retrain models or overwrite `clara.db` merely to make documentation numbers match.
- Do not redesign CLARA in React or replace Streamlit.
- Do not add live cloud-provider integrations, authentication, autonomous remediation, or other production features.
- Do not require a paid hosting plan.

## Anti-Goals

- A hosted page that differs from the submitted presentation.
- A demo that requires terminal setup, a Gemini key, or network API availability after deployment.
- Inflated or ambiguous claims such as treating all recommendation savings as FinOps waste.
- Committing `.env`, API keys, temporary runtimes, caches, logs, or backup databases.

## Constraints

- Active database: `clara.db`; ignore `clara.db.live_backup`.
- Preserve the verified `$220.87` total recommendation savings unless a database-backed explanation requires a correction.
- Preserve verified anomaly evaluation results: precision 82.35%, recall 93.33%, F1 0.8750, 15 injected anomalies, and 17 predicted anomalies.
- Preserve the production database hash: `DE271EA91DA0DF6C2A22C9D967684574FBD3F63FE25B6CAB8A5C07C7B91F6BD8`.
- Never commit `.env` or an API key.
- The hosted application must run from the public GitHub repository using Streamlit Community Cloud.

## Approaches Considered

### Direct commits to `main`

This is fastest but exposes incomplete intermediate states and makes rollback harder during synchronization.

### Submission branch followed by merge

Chosen approach. Create `submission-ready`, push small reviewable commits, verify the complete branch, then merge it into `main`. This keeps the public default branch stable until the release candidate is ready.

### Patch the old GitHub implementation

Rejected because the remote implementation uses deprecated dependencies, stale thresholds, obsolete ETL instructions, and does not contain the verified final project behavior. The local handoff is the stronger source of truth.

## Design

### 1. Repository synchronization

Use the current local handoff as the source tree. Exclude local audit artifacts, virtual environments, caches, logs, `.env`, `clara.db.live_backup`, and document-generation intermediates that are not needed for evaluation. Include `clara.db` explicitly even though general database patterns remain ignored.

### 2. Metric semantics

Use these database-backed meanings everywhere:

- Total fleet: 300 instances.
- Provider distribution: AWS 155, Azure 88, GCP 57.
- Injected ground-truth anomalies: 15.
- Model-predicted anomalies at threshold 65: 17.
- Critical instances: 1 at score >= 80.
- High-risk instances: 6 at 60 <= score < 80.
- Cost-recommendation savings: $184.58 per month.
- Total recommendation savings: $220.87 per month.

Dashboard labels, README, demo guide, presentation, report-supporting Markdown, and viva material must not conflate these quantities.

### 3. Coverage claim

Define coverage over the application packages that the tests are intended to validate, excluding tests, packaging scripts, generated-document scripts, and deployment helpers. Add an explicit coverage configuration and acceptance threshold only if the resulting measurement is honest and reproducible. If it remains below 80%, update all claims to the measured value rather than manipulating exclusions solely to reach a target.

### 4. Dashboard reliability

Keep the existing four-page Streamlit application. Add or update regression tests for metric labels and values before changing application behavior. Ensure every page runs from a clean process with `clara.db`, renders without exceptions, and handles a missing Gemini key.

### 5. Deployment

Provide a root-level dependency definition compatible with a supported Streamlit Community Cloud Python version. Add Streamlit configuration only where it improves deterministic startup. The entry point remains `dashboard/app.py`. The repository must contain every runtime file required by the hosted app.

Deployment is performed only after `main` contains the verified release. Account authorization or login that cannot be safely automated will be handed to the user at the exact action where it is required.

### 6. Documentation and presentation

Update the README and final Markdown documentation first. Update generated Word, PDF, and PowerPoint artifacts only through their proper artifact workflows if their visible claims need correction. Fill the final presentation date and remove stale machine-specific paths and nonexistent commands. Produce a concise demo sequence that opens the hosted site first and keeps local execution and tests as backup evidence.

### 7. Verification and release

Before merge:

- Run `pytest -v` and require all tests to pass.
- Run the defined coverage command and record the honest percentage.
- Run `python -m analytics.evaluate_anomaly_model` and verify the documented metrics.
- Query `clara.db` read-only for fleet, provider, risk, anomaly, and savings totals.
- Run all Streamlit pages through Streamlit's application testing API.
- Compare the `clara.db` hash before and after verification.
- Scan tracked files for secrets and excluded audit artifacts.
- List all changed files and commits.

Merge `submission-ready` into `main` only after these checks succeed.

## Builder Decisions

- Prefer correcting labels and documents over changing verified data.
- Prefer the smallest dependency or configuration change that deploys successfully.
- Keep visual changes modest and presentation-focused; reliability and clarity take priority over a redesign.
- Commit by coherent unit: repository hygiene, metric semantics/tests, documentation, deployment, and final release verification.

