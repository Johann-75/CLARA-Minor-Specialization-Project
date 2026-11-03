# CLARA Comprehensive Viva Voce Questions & Answers Guide

**System:** CLARA: Cloud-Linked Evaluation and Risk Assessment using Predictive Analytics and Business Intelligence  
**Course Code:** CSE 4191 – Minor Specialization Mini Project (Data Analytics)  
**Academic Year:** 2026 – 2027  
**Department:** Computer Science & Engineering, Manipal Institute of Technology Bengaluru  
**Audience:** University Project Evaluators, External Examiners, and Student Defense Preparation  

---

## SECTION 1: Architecture, Storage & Ingestion Decisions

### Q1: Why did you choose DuckDB over traditional client-server databases like PostgreSQL or MySQL?
**Answer:** DuckDB was selected because it is an **embedded, columnar analytical database (OLAP)** designed specifically for vectorized data science workflows:
1. It runs in-process inside Python, eliminating the need to install, configure, manage, and monitor external server background daemons or listen on open network ports;
2. Its vectorized execution engine processes analytical queries across 27,000 metrics records with sub-second in-process execution;
3. It enables clean, foolproof test isolation: unit tests spin up isolated temporary databases in `tmp_path` without port conflicts;
4. It provides direct, zero-copy interoperability with Apache Arrow and Pandas DataFrames.

### Q2: Why did you evolve the architecture away from PostgreSQL, SQLAlchemy, Random Forest, SHAP, and River proposed in Phase 1?
**Answer:** During our engineering audits across Phase 1 and Phase 2, we evaluated each component against real-world performance, maintainability, and operational stability:
- **PostgreSQL / SQLAlchemy:** Required background server daemons and network sockets, complicating reproducible student evaluation and CI/CD testing; DuckDB replaced it with zero performance loss.
- **Supervised Random Forest & River:** Cloud operations lack vast repositories of clean, labeled historical anomaly data. Supervised learning leads to overfitting and fails to generalize to novel attacks. Unsupervised Isolation Forest was adopted instead.
- **SHAP on Security Classifier:** Using a black-box classifier and approximating it with SHAP values created unnecessary opacity. Security teams require transparent, deterministic posture scoring based on observable encryption, IAM, exposure, vulnerability-age and security-event indicators.
- **Linear Regression for Cost:** Simple linear regression fails to account for multidimensional resource utilization (e.g., low CPU but high RAM). Unsupervised K-Means clustering was adopted to isolate genuine over-provisioned idle instances.

### Q3: How is the synthetic dataset structured, and how does it simulate real-world multi-cloud telemetry?
**Answer:** The active database contains 300 instances across AWS, Azure, and GCP, distributed as AWS 155 / Azure 88 / GCP 57 across general-purpose, compute-optimized, and memory-optimized families. It contains 90 days of daily telemetry (27,000 records total). Telemetry incorporates diurnal curves combined with Gaussian stochastic noise.

### Q4: What is the purpose of `anomaly_manifest.json`, and how do you prevent data leakage during training?
**Answer:** The manifest logs the exact ground-truth metadata (instance ID, anomaly category, start day, duration, affected metrics) for the 15 injected anomaly scenarios. To prevent data leakage, **the manifest is strictly isolated in the data directory and is never accessed or imported by feature engineering, Isolation Forest training, calibration, threshold selection, or inference**. Ground-truth labels are loaded exclusively by the external evaluation script (`evaluate_anomaly_model.py`) post-inference to score precision and recall.

---

## SECTION 2: Anomaly Detection & Time-Series Feature Engineering

### Q5: What algorithm is used for anomaly detection, and why?
**Answer:** We use an **Isolation Forest** ensemble (150 estimators, contamination=0.05, random_state=42). Isolation Forests isolate anomalous observations by recursively selecting random feature splits. Because anomalous points require significantly fewer partitions to be isolated, they exhibit shorter path lengths in the trees. It has linear time complexity O(n), low memory overhead, and resists masking effects in high-dimensional feature spaces.

### Q6: Why did basic point-in-time metrics fail, and what 11 time-series features were engineered?
**Answer:** Cloud anomalies are temporal: a sudden CPU burst looks like a normal batch job, while a slow memory leak never triggers a static threshold until the server crashes. We engineered 11 rolling time-series features:
1. `max_robust_z_cpu`: Outlier CPU spike using Median Absolute Deviation (MAD);
2. `max_robust_z_mem`: Outlier RAM consumption via MAD;
3. `max_robust_z_net`: Massive data transfer via MAD;
4. `max_robust_z_disk`: Disk IOPS saturation via MAD;
5. `max_day_to_day_cpu`: Maximum absolute daily difference over 90 days;
6. `peak_to_median_net`: Burstiness ratio of peak outbound traffic over median traffic;
7. `dev_7d_vs_30d_cpu`: Divergence between 7-day short-term mean and 30-day baseline mean;
8. `dev_7d_vs_30d_net`: Divergence between short and long-term network throughput;
9. `max_rolling_slope_mem`: Maximum linear regression slope over a rolling 14-day window to catch gradual leaks;
10. `combined_spike_signal`: Weighted multi-resource shock (`0.4*Z_cpu + 0.3*Z_mem + 0.3*Z_net`);
11. `net_disk_interaction`: Correlated disk reading and network exfiltration (`log1p(net) * log1p(iops)`).

### Q7: Why use Median Absolute Deviation (MAD) instead of standard deviation for robust z-scores?
**Answer:** Standard deviation is extremely sensitive to extreme outliers: a single massive network burst dramatically inflates the sample standard deviation, shrinking the z-score of subsequent anomalies and causing masking. The Median Absolute Deviation ($MAD = \text{median}(|X - \text{median}(X)|)$) is a robust estimator with a 50% breakdown point, ensuring that outlier spikes cannot distort the baseline scale.

### Q8: What were your quantitative evaluation results on the seed-42 anomaly corpus?
**Answer:** At the production operational threshold of 65.0, our detector achieved:
- **Precision:** 82.35% (exceeding the ≥ 80.0% acceptance criterion);
- **Recall:** 93.33% (14 out of 15 true positives, exceeding the ≥ 85.0% criterion);
- **F1-Score:** 0.8750;
- **Category detection breadth: all 5 anomaly categories had at least one detected instance:**
  - `brute_force`: 3/3 — 100.0%
  - `cpu_spike`: 3/3 — 100.0%
  - `memory_leak`: 2/3 — 66.7%
  - `misconfiguration`: 3/3 — 100.0%
  - `network_exfiltration`: 3/3 — 100.0%

### Q9: Why is the anomaly classification threshold set at 65.0, and does it correspond to CVSS?
**Answer:** The 65.0 threshold is a **project-defined operational triage threshold** chosen to balance high recall with low false alarms (3 false positives across 285 normal instances). It is an operational decision threshold on a calibrated 0–100 scale and does **not** map to CVSS or NIST severity intervals, which use different scales (0–10 for CVSS) and vulnerability-specific metrics.

---

## SECTION 3: FinOps Rightsizing & Cost Optimization

### Q10: How does CLARA identify cost waste without static rules?
**Answer:** We implement unsupervised **K-Means clustering** ($k=3$) across 30-day rolling average CPU utilization, peak CPU utilization, average memory utilization, and baseline daily spend. This partitions the fleet into:
- **Cluster 0 (Over-Provisioned / Idle):** Mean CPU 7.8%, Mean RAM 14.2%;
- **Cluster 1 (Balanced Workloads):** Mean CPU 48.6%, Mean RAM 62.4%;
- **Cluster 2 (Constrained / High Load):** Mean CPU 84.2%, Mean RAM 88.1%.

### Q11: How is Actionable Cost Waste calculated mathematically?
**Answer:** For instances assigned to the over-provisioned cluster, actionable waste is computed as:
$$\text{Actionable Waste} = \left(1 - \max\left(\frac{\text{AvgCPU}}{50}, \frac{\text{AvgRAM}}{60}\right)\right) \times \text{ProjectedMonthlySpend}$$
This ensures that waste reflects unused capacity while preserving a safety buffer of 50% CPU and 60% RAM for production traffic spikes. The stored recommendations contain **$184.58/month in cost and rightsizing savings** and **$220.87/month across all recommendation types**.

---

## SECTION 4: Security Posture & Composite Risk Formulation

### Q12: How is the Security Posture Score calculated?
**Answer:** It is calculated deterministically on a 0–100 scale based on observable encryption, IAM, exposure, vulnerability-age and security-event indicators:
- Unpatched Vulnerabilities: Vulnerability age and severity indicators contribute up to 50 points;
- Unrestricted Public Ingress on SSH (22) or RDP (3389): 25 points;
- Administrative IAM Permission Level: 20 points;
- Security Events & Encryption: Active failed-login bursts or disabled encryption contribute up to 15 points;
- Clamped strictly to a maximum of 100.0.

### Q13: What is the exact formula for Overall / Composite Risk?
**Answer:**
$$\text{Composite Risk} = (0.50 \times \text{Security Score}) + (0.30 \times \text{Telemetry Anomaly Score}) + (0.20 \times \text{Cost Waste Score})$$
Security is weighted highest (50%) because unpatched vulnerabilities and exposed ports represent acute attack vectors. Telemetry anomalies carry 30% because active system shocks impact availability. Cost waste carries 20% because financial inefficiency impacts operational budgets.

### Q14: What are the centralized operational risk tiers, and how are missing scores handled?
**Answer:**
- **Critical:** Score $\ge 80.0$ (Crimson Red);
- **High:** $60.0 \le \text{Score} < 80.0$ (Amber Orange);
- **Medium:** $40.0 \le \text{Score} < 60.0$ (Yellow);
- **Low:** $0.0 \le \text{Score} < 40.0$ (Emerald Green);
- **Unknown:** NULL, NaN, negative, or invalid score (Neutral Slate Gray).
Under semantic hardening, invalid or missing scores are explicitly classified as UNKNOWN to prevent silent misclassification as Low risk.

---

## SECTION 5: Generative AI, Google GenAI SDK & Provenance

### Q15: Why did you migrate from `google-generativeai` to the modern `google-genai` SDK?
**Answer:** Google officially deprecated `google-generativeai` in late 2024 in favor of the unified `google-genai` SDK. The new SDK supports native Pydantic schema validation, modern Gemini 2.5 and 3.8 endpoints (`gemini-3.8-flash`), robust streaming, and cleaner configuration.

### Q16: How do you prevent LLM hallucinations of invalid instance IDs or unrealistic savings?
**Answer:** We implement a two-stage anti-hallucination guard:
1. **Pydantic Schema Validation:** The model response must strictly conform to `RecommendationList`, where `estimated_monthly_savings` is bounded as non-negative (`ge=0.0`) and categories are restricted to literal enums (`cost`, `security`, `performance`, `reliability`);
2. **Instance Candidate Verification:** Application code validates every returned `instance_id` against the candidate set queried from DuckDB. Any recommendation with a fabricated or unrequested ID is rejected.

### Q17: What is Application-Controlled Provenance, and why is it essential?
**Answer:** Application-controlled provenance means **we never allow Gemini to declare its own source, model name, or fallback state**. Prompt injection or LLM drift could cause a model to falsely claim it is an offline rule engine or vice versa. The application orchestrator explicitly writes:
- For successful Gemini responses: `generation_source='gemini'`, `model_name='gemini-3.8-flash'`, `fallback_reason=NULL`;
- For fallback responses: `generation_source='offline_fallback'`, `model_name='deterministic_rule_engine'`, `fallback_reason='missing_key' | 'api_error'`.

### Q18: What happens if the Gemini API key is missing or the external API is down?
**Answer:** The pipeline remains operational in the tested missing-key and API-failure scenarios by using a clearly labelled deterministic fallback stamped with `generation_source='offline_fallback'` and `model_name='deterministic_rule_engine'`.

---

## SECTION 6: Software Engineering, Testing & CI/CD

### Q19: How did you implement test isolation, and why was it a critical requirement?
**Answer:** In Phase 1, tests were writing directly to the project root `clara.db` and CSV files, which risked corrupting live demonstration data. We re-engineered the test harness in `tests/conftest.py` using session-scoped pytest `tmp_path` fixtures. All CSV generation and DuckDB operations during testing occur inside an isolated temporary directory. Running the 82 tests leaves the production `clara.db` database bit-for-bit identical (SHA256: `DE271EA91DA0DF6C2A22C9D967684574FBD3F63FE25B6CAB8A5C07C7B91F6BD8`).

### Q20: What is your test suite pass rate and code coverage?
**Answer:** The complete test suite passes and achieves **67% statement coverage across all configured runtime application packages**. Tests mock external Gemini calls and execute without an API key. Release-readiness tests additionally verify deployment files, metric semantics, documentation consistency, and repository hygiene.

---

## SECTION 7: System Boundaries, Ethics & Limitations

### Q21: Why is CLARA an advisory decision-support system rather than an autonomous self-healing agent?
**Answer:** In production multi-cloud environments, automated write actions (e.g., stopping an EC2 instance, deleting an Azure disk, or modifying a firewall rule) carry catastrophic risks of downtime, cascading failures, or compliance violations if triggered by false positives. CLARA prioritizes triage, calculates risk, and drafts verified runbooks, leaving the execution decision strictly to human cloud engineers (human-in-the-loop).

### Q22: What are the primary limitations of the current implementation?
**Answer:**
1. **Synthetic Telemetry:** While statistically realistic, synthetic telemetry cannot capture unpredictable production phenomena such as hypervisor hardware faults, packet drops, or provider-side throttling;
2. **Static Weighting:** The composite risk weights (0.5/0.3/0.2) are fixed. In dev/test environments, cost waste may warrant higher priority than security hardening;
3. **API Latency:** External Gemini API calls take 1.5–3.5s per batch, making it unsuitable for sub-second real-time alerting (which is handled by the deterministic engine).
