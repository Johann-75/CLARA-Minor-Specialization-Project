# CLARA Submission-Ready Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Synchronize the verified local CLARA implementation to GitHub, make all evaluator-visible claims agree with `clara.db`, and deploy a reliable Streamlit Community Cloud demonstration.

**Architecture:** Treat the local handoff and immutable `clara.db` as the release source. Correct semantics through tests, labels, configuration, and documentation; publish changes through a protected `submission-ready` branch; merge only after database, test, UI, and secret-scan gates pass.

**Tech Stack:** Python 3.11, Streamlit 1.36, DuckDB 1.0, pytest/pytest-cov, Plotly, Google GenAI SDK, GitHub, Streamlit Community Cloud

**Spec:** `docs/superpowers/specs/2026-11-03-submission-ready-design.md`

## Global Constraints

- Never regenerate the dataset or overwrite `clara.db`.
- Ignore and do not publish `clara.db.live_backup`.
- Preserve database SHA-256 `DE271EA91DA0DF6C2A22C9D967684574FBD3F63FE25B6CAB8A5C07C7B91F6BD8`.
- Preserve total recommendation savings `$220.87`; label cost-only savings `$184.58` separately.
- Preserve 15 injected anomalies and 17 model-predicted anomalies as distinct metrics.
- Never commit `.env`, API keys, local runtimes, caches, coverage data, or logs.
- The app must run without live Gemini access.
- All 75 existing tests must pass before merge.

## Review Focus

- Missing `clara.db`: deployment should display an actionable error rather than crash; pin with the existing database-missing dashboard tests and Streamlit AppTest.
- Missing Gemini key: stored recommendations and fallback behavior must remain usable; pin with `test_missing_api_key_triggers_offline_fallback`.
- Filtered dashboard subsets: cost-only and total savings must remain distinct under provider/region filters; pin with new overview-metric regression tests.
- Unsupported dependency resolution: deployment requirements must install under Python 3.11; pin with a clean import smoke test.
- Stale or secret-bearing files: tracked release contents must exclude `.env`, backup database, runtimes, caches, and logs; pin with a release-manifest audit.

---

### Task 1: Release hygiene and branch foundation

**Files:**
- Modify: `.gitignore`
- Create: `.streamlit/config.toml`
- Create: `.python-version`
- Test: `tests/test_release_readiness.py`

**Interfaces:**
- Consumes: the local repository tree and active `clara.db`.
- Produces: `audit_release_tree(root: Path) -> list[str]` test helper expectations and a deployable tracked-file policy.

- [ ] **Step 1: Write a failing release-tree test**

Add tests asserting that `.env`, `clara.db.live_backup`, `.venv`, `.python311`, `.tmp_pip`, coverage files, caches, and Streamlit logs are excluded while `clara.db` is explicitly allowed.

- [ ] **Step 2: Run the test and verify the current ignore policy fails because `clara.db` is ignored**

Run: `.\.python311\python.exe -m pytest tests/test_release_readiness.py -v`

- [ ] **Step 3: Update release configuration**

Modify `.gitignore` to retain `*.db` protection while unignoring `clara.db`; add `.python-version` with `3.11`; add headless Streamlit configuration without credentials.

- [ ] **Step 4: Run the release-tree test and verify it passes**

- [ ] **Step 5: Create GitHub branch `submission-ready` from current `main` and commit the release foundation**

Commit message: `chore: prepare submission deployment foundation`

### Task 2: Pin evaluator-visible metric semantics

**Files:**
- Modify: `tests/test_dashboard.py`
- Modify: `dashboard/app.py`
- Modify: `dashboard/pages/1_Overview.py`
- Modify: `dashboard/utils/data_access.py` only if required by failing behavior

**Interfaces:**
- Consumes: `get_overview_metrics(provider: str | None, region: str | None) -> dict`.
- Produces: stable UI labels for `total_monthly_waste_usd` and `total_potential_savings_usd`.

- [ ] **Step 1: Add failing tests for metric names and database-backed values**

Assert the unfiltered active-database semantics: 300 instances, 1 critical, 6 high, `$184.58` cost-recommendation savings, and `$220.87` total recommendation savings. Assert UI copy uses “Cost Recommendation Savings” and “All Recommendation Savings” so neither is described as generic waste.

- [ ] **Step 2: Run focused dashboard tests and verify label assertions fail**

Run: `.\.python311\python.exe -m pytest tests/test_dashboard.py -v`

- [ ] **Step 3: Update the two Streamlit pages with precise labels and help text**

Do not change the query totals or database.

- [ ] **Step 4: Run focused tests and all Streamlit AppTest entry points**

Expected: no exceptions and correct metric values.

- [ ] **Step 5: Commit and push the metric semantics change to `submission-ready`**

Commit message: `fix: align dashboard metrics with verified database`

### Task 3: Make coverage measurement honest and reproducible

**Files:**
- Create: `.coveragerc`
- Modify: `pytest.ini`
- Modify: `tests/test_release_readiness.py`
- Modify: `README.md`
- Modify: `docs/final/REQUIREMENTS_TRACEABILITY_MATRIX.md`

**Interfaces:**
- Produces: one documented coverage command and its measured percentage over runtime application packages.

- [ ] **Step 1: Add a failing test that requires an explicit coverage source configuration**

Assert source packages are `analytics`, `dashboard`, `data_generator`, `genai`, and `warehouse`; exclude tests, document generators, packaging helpers, temporary runtimes, and generated files.

- [ ] **Step 2: Run the readiness test and verify `.coveragerc` is missing**

- [ ] **Step 3: Add `.coveragerc` and a stable pytest coverage command**

Do not exclude poorly covered runtime modules solely to reach 80%.

- [ ] **Step 4: Run coverage and record the honest measured result**

Run: `.\.python311\python.exe -m pytest --cov --cov-report=term-missing`

- [ ] **Step 5: Update coverage claims to the measured result and commit**

Commit message: `test: define honest application coverage scope`

### Task 4: Correct submission documentation and demo guidance

**Files:**
- Modify: `README.md`
- Modify: `docs/final/PROJECT_OVERVIEW.md`
- Modify: `docs/final/DEMO_GUIDE.md`
- Modify: `docs/final/INSTALLATION_GUIDE.md`
- Modify: `docs/final/VIVA_QUESTIONS_AND_ANSWERS.md`
- Modify: `docs/final/CLARA_Presentation_Script.md`
- Modify: `docs/final/screenshots/README.md`
- Test: `tests/test_release_readiness.py`

**Interfaces:**
- Consumes: verified metric constants from the approved design and measured coverage from Task 3.
- Produces: evaluator-facing instructions consistent with the hosted and local application.

- [ ] **Step 1: Add failing documentation-consistency tests**

Reject the machine-specific Nandan path, nonexistent `python -m warehouse.db`, unqualified “$220.87 actionable cost waste,” claims of balanced 100/100/100 providers, claims that 15 is the predicted-anomaly count, placeholder final dates, and stale coverage percentages.

- [ ] **Step 2: Run the readiness test and confirm the stale claims are detected**

- [ ] **Step 3: Rewrite the affected Markdown sections**

Use provider distribution AWS 155 / Azure 88 / GCP 57; 15 injected / 17 predicted; `$184.58` cost-only / `$220.87` total; correct portable Windows setup commands; hosted-first demo flow; November 3, 2026 date.

- [ ] **Step 4: Run documentation-consistency tests**

- [ ] **Step 5: Commit and push documentation updates**

Commit message: `docs: align submission claims and demo instructions`

### Task 5: Update final presentation and report deliverables

**Files:**
- Modify: `docs/final/CLARA_Final_Presentation.pptx`
- Modify: `docs/final/CLARA_Final_Presentation.pdf`
- Modify: `docs/final/CLARA_Final_Project_Report.docx`
- Modify: `docs/final/CLARA_Final_Project_Report.pdf`
- Test: rendered slide/page inspections and `tests/test_release_readiness.py`

**Interfaces:**
- Consumes: corrected Markdown claims and the existing branded artifacts.
- Produces: final binary deliverables with matching evaluator-visible numbers and date.

- [ ] **Step 1: Add artifact text-extraction checks that fail on stale claims**

Check for the date placeholder, 100/100/100 provider claim, `$220.87` described as cost-only waste, and stale coverage.

- [ ] **Step 2: Render and inspect the existing presentation and report**

Use the presentation and document artifact workflows; preserve layout and branding.

- [ ] **Step 3: Update visible claims and regenerate the corresponding PDFs**

- [ ] **Step 4: Render every changed page/slide and verify text fit and consistency**

- [ ] **Step 5: Commit and push final evaluator artifacts**

Commit message: `docs: refresh final submission artifacts`

### Task 6: Full verification, GitHub release, and Streamlit deployment

**Files:**
- Modify: GitHub branch/ref metadata only after verification
- Create: `docs/final/SUBMISSION_HANDOFF.md`

**Interfaces:**
- Consumes: Tasks 1–5 release candidate.
- Produces: verified `main`, hosted Streamlit URL, and presenter runbook.

- [ ] **Step 1: Record the production database hash and run `pytest -v`**

Expected: 75 existing tests plus new readiness tests pass.

- [ ] **Step 2: Run coverage, anomaly evaluation, read-only database audit, Streamlit AppTest, and import smoke test**

Expected anomaly metrics: precision 82.35%, recall 93.33%, F1 0.8750.

- [ ] **Step 3: Recheck the production database hash**

Expected: exact match with the pre-test hash.

- [ ] **Step 4: Audit the GitHub branch for secrets, missing runtime files, and unwanted artifacts**

- [ ] **Step 5: Add the final handoff with hosted-first demo steps and offline fallback steps**

- [ ] **Step 6: Commit and push verification handoff**

Commit message: `release: finalize CLARA submission handoff`

- [ ] **Step 7: Merge `submission-ready` into `main` after the checks pass**

- [ ] **Step 8: Deploy `dashboard/app.py` from `main` to Streamlit Community Cloud**

If login or repository authorization is required, pause at that exact action for the user to complete it.

- [ ] **Step 9: Open the public URL and verify all four pages**

- [ ] **Step 10: Deliver the URL, commit list, changed-file list, verification results, and concise explanation**

