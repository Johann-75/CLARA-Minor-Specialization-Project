# CLARA: Final Phase Presentation Script and Defense Guide
**Canonical Title:** CLARA — Cloud-Linked Evaluation and Risk Assessment  
**Course Code:** CSE 4191 – Minor Specialization Mini Project (Data Analytics)  
**Institution:** Manipal Institute of Technology Bengaluru  
**Academic Year:** 2026–2027  
**Team:** Johann Mathew Sajan, Nandan Murali, Abhijay Gupta, Arshia Gali  
**Supervisor:** Dr. Geetabai S Hukkeri  

---

## Slide 1: CLARA: Cloud-Linked Evaluation and Risk Assessment using Predictive Analytics and Business Intelligence
*A Unified Platform for Multi-Cloud Observability, Multi-Modal Anomaly Detection, FinOps Rightsizing, and Generative AI Operational Guidance*

### Spoken Delivery Script
> "Good morning respected members of the evaluation committee, project guide Dr. Geetabai Hukkeri, and faculty members. Welcome to the final phase review of our minor specialization project titled CLARA: Cloud-Linked Evaluation and Risk Assessment. Our team members are Johann Mathew Sajan, Nandan Murali, Abhijay Gupta, and Arshia Gali. Over the past two semesters, under the data analytics specialization, we set out to build an end-to-end, multi-cloud observability, risk assessment, and FinOps platform that combines explainable machine learning with modern Generative AI to provide trustworthy operational decision support."

### Key Visual Bullets
- Manipal Institute of Technology Bengaluru — Department of Computer Science & Engineering
- CSE 4191: Minor Specialization Mini Project (Data Analytics) — Final Phase Review
Date: November 3, 2026 | Academic Year: 2026–2027
- Students: Johann Mathew Sajan (235890104), Nandan Murali (235890114), Abhijay Gupta (235890206), Arshia Gali (235890070)
- Under the Supervision of: Dr. Geetabai S Hukkeri, Assistant Professor, Dept. of CSE, MIT Bengaluru

---

## Slide 2: Presentation Outline
*Systematic Walkthrough of Problem, Methodology, Results, and Verification*

### Spoken Delivery Script
> "Here is the roadmap for today's presentation. We will begin by defining the operational problem and our core design boundary as an advisory decision-support system. Next, we will review the literature and trace the evolution of our architecture from the Phase 1 proposal to the final verified implementation. We will detail each layer of CLARA—from synthetic multi-cloud data generation and embedded DuckDB warehousing to our 11-feature Isolation Forest detector, FinOps rightsizing, and dual-engine Gemini recommendation system. Finally, we will demonstrate our experimental results, test coverage, and discuss limitations and future extensions."

### Key Visual Bullets
- 1. Problem Statement & Motivation — The Multi-Cloud Operational Dilemma
- 2. Project Objectives & Architectural Boundaries (Advisory Decision-Support)
- 3. Literature Review & Comparative Analysis of Existing Platforms
- 4. System Architecture & Architectural Evolution from Phase 1 Proposal
- 5. Synthetic Multi-Cloud Data Generation & Embedded DuckDB Warehouse
- 6. Multi-Modal Anomaly Detection Engine (11 Features + Isolation Forest)
- 7. Explainable Security Posture & FinOps Rightsizing Engines
- 8. Composite Risk Formulation & Centralized Operational Severity Tiers
- 9. Dual-Engine GenAI Advisory Architecture (Gemini 3.8 Flash + Offline Fallback)
- 10. Presentation Layer: Interactive Multi-Page Streamlit Dashboard
- 11. Experimental Results: Confusion Matrix, Honest Recall Breakdown, and Cost Waste
- 12. Automated Test Suite, Test Isolation Architecture, and Statement Coverage
- 13. System Limitations, Ethical Governance, Future Roadmap, and Conclusion

---

## Slide 3: Problem Statement & Motivation
*The Trilemma of Multi-Cloud Observability, Security Risk, and Cloud Spend*

### Spoken Delivery Script
> "Modern enterprises deploy workloads across multiple cloud providers to avoid vendor lock-in and meet regulatory standards. However, this creates severe operational fragmentation. Telemetry streams in AWS CloudWatch, Azure Monitor, and GCP Cloud Operations are completely isolated. Alert fatigue is endemic: static threshold alerts bury critical signals like slow memory leaks. Furthermore, cost management is detached from security, and modern generative AI tools often hallucinate or fail when external APIs disconnect. CLARA directly addresses this trilemma by unifying multi-cloud telemetry, explainable risk scoring, and structured GenAI advisory support."

### Key Visual Bullets
- Multi-Cloud Heterogeneity: Enterprise workloads span AWS, Azure, and GCP, resulting in fragmented dashboards, incompatible metric schemas, and isolated IAM policies.
- Alert Fatigue & Naive Thresholds: Traditional monitoring systems generate hundreds of false alarms daily, overwhelming DevOps teams while masking gradual memory leaks and low-profile brute-force activity.
- Detached FinOps: Cloud billing tools track financial overruns post-facto without correlating wasted spend to idle instances or misconfigured infrastructure.
- Ungrounded GenAI: Standard LLM chatbots hallucinate non-existent resource IDs, lack structured schemas, and fail during external API downtime.
- Core Opportunity: A unified platform that ingests multi-cloud telemetry into an embedded analytical warehouse, executes explainable ML risk scoring, and pairs structured Gemini recommendations with deterministic offline fallbacks.

---

## Slide 4: Project Objectives & Design Boundaries
*Core Technical Deliverables and Human-in-the-Loop Operational Scope*

### Spoken Delivery Script
> "Our engineering goals were concrete: ingest 27,000 metrics records across 300 multi-cloud instances; build an embedded DuckDB warehouse with in-process analytical execution; achieve at least 80% precision and 85% recall on an isolated anomaly corpus; isolate actionable monthly cost waste using K-Means; and deploy a production-ready dual-engine Gemini recommendation system. Crucially, we established a strict architectural boundary: CLARA is an advisory decision-support system, not an autonomous remediation bot. In enterprise infrastructure, automated write actions can trigger disastrous outages. CLARA empowers human engineers with verified, explainable playbooks rather than executing risky unattended changes."

### Key Visual Bullets
- Objective 1: Multi-Cloud Telemetry Ingestion — Model 300 instances across AWS, Azure, and GCP over a 90-day window (27,000 metrics records) with 15 injected anomaly scenarios.
- Objective 2: Embedded Analytical Warehousing — Deploy DuckDB (clara.db) for in-process vectorized OLAP queries without external server daemons.
- Objective 3: Multi-Modal Anomaly Detection — Engineer 11 rolling time-series features with Isolation Forest to achieve ≥ 80% Precision and ≥ 85% Recall on isolated ground-truth data.
- Objective 4: Explainable FinOps & Security Scoring — Unsupervised K-Means clustering for rightsizing and deterministic posture scoring based on observable indicators.
- Objective 5: Dual-Engine GenAI Advisory Architecture — Modern Google GenAI SDK (gemini-3.8-flash) with Pydantic validation, provenance tracking, and deterministic offline rule fallback.
- Critical Design Boundary: CLARA is strictly an ADVISORY DECISION-SUPPORT SYSTEM. It provides explainable guidance and projected savings; human cloud engineers retain ultimate operational authority over infrastructure changes.

---

## Slide 5: Literature Review & Research Gaps
*Benchmarking CLARA Against Commercial and Open-Source Management Tools*

### Spoken Delivery Script
> "In our literature review, we analyzed leading enterprise systems. Datadog excels at metrics but does not evaluate security posture or provide structured LLM playbooks. Prisma Cloud checks security compliance but lacks runtime time-series anomaly detection. FinOps tools like Kubecost focus strictly on billing without understanding security posture. And generic chatbots lack structured schema guarantees and hallucinate non-existent resource IDs. CLARA fills this exact research and tooling gap by unifying all four dimensions into a single, reproducible, embedded architecture."

### Key Visual Bullets
- Commercial Telemetry (Datadog, Dynatrace): Excellent metric ingestion via proprietary agents, but lacks integrated multi-cloud compliance scoring and structured generative AI runbooks.
- Cloud Security Posture Management (Prisma Cloud, Wiz): Comprehensive CVE and IAM posture evaluation, but lacks real-time time-series telemetry anomaly detection and FinOps rightsizing.
- Dedicated FinOps (Kubecost, CloudHealth): Focuses strictly on cost allocation post-facto; does not correlate spend to security vulnerabilities or runtime performance degradation.
- Basic LLM Chatbots: Produce unstructured natural language prone to hallucinating resource IDs, unable to operate offline, and lack schema guarantees.
- Identified Research Gap: Lack of a unified, lightweight platform that combines embedded columnar warehousing, multi-modal time-series anomaly detection, explainable risk scoring, and structured GenAI advisory playbooks with offline fallback.

---

## Slide 6: System Architecture Overview
*Four-Tier Decoupled Platform: Ingestion, Warehouse, Analytics, Presentation*

### Spoken Delivery Script
> "Slide 6 presents CLARA's four-tier architecture. Tier 1 handles multi-cloud telemetry ingestion across AWS, Azure, and GCP, modeling 300 instances and 15 ground-truth anomaly scenarios. Tier 2 is our persistence layer: an embedded DuckDB columnar warehouse that processes 27,000 records in-process with zero server daemons. Tier 3 houses our machine learning and risk scoring engines: Isolation Forest with 11 domain features, K-Means clustering for rightsizing, and an explainable security posture scorer. Finally, Tier 4 delivers decision support via our dual-engine Gemini integration and four-page Streamlit business intelligence dashboard."

### Key Visual Bullets
- Tier 1: Multi-Cloud Ingestion — AWS, Azure, GCP synthetic telemetry generation with diurnal curves, noise, and 15 ground-truth anomaly injections.
- Tier 2: Embedded Analytical Warehouse — In-process DuckDB columnar store executing vectorized analytical aggregations with zero server daemons.
- Tier 3: Analytics & Risk Engines — 11-feature Isolation Forest anomaly detector, K-Means FinOps rightsizing, and deterministic security posture scorer.
- Tier 4: Presentation & AI Advisory — Modern Google GenAI SDK (gemini-3.8-flash) + offline fallback engine, visual 4-page Streamlit BI dashboard.

---

## Slide 7: Architectural Evolution: Proposal vs Implemented
*Engineering Justification for Strategic Refinements Across Project Phases*

### Spoken Delivery Script
> "A key requirement of this final submission is documenting the architectural evolution from our Phase 1 proposal to the final verified implementation. Rather than maintaining a heavy PostgreSQL server, we migrated to DuckDB, eliminating network daemon dependencies and enabling clean test isolation. For anomaly detection, supervised Random Forest was impractical because real-world cloud anomalies lack clean labels; we adopted Isolation Forest augmented with 11 rolling features. For security, deterministic rule scoring replaced black-box classifiers to guarantee complete transparency. For FinOps, K-Means clustering replaced simple linear regression. And for GenAI, we modernized from the deprecated SDK to the current google-genai library with strict Pydantic validation and deterministic offline fallback."

### Key Visual Bullets
- Data Warehouse: Phase 1 proposed PostgreSQL + SQLAlchemy. Evolved to Embedded DuckDB (clara.db) for in-process OLAP, zero network daemon overhead, and seamless test isolation.
- Anomaly Detection: Phase 1 proposed supervised Random Forest and River online learning. Evolved to Isolation Forest + 11 engineered time-series features for unsupervised anomaly isolation without requiring labeled production training data.
- Security Risk Scorer: Phase 1 proposed opaque classifier with SHAP explainability. Evolved to deterministic posture scoring based on observable encryption, IAM, exposure, vulnerability-age and security-event indicators.
- Cost Optimization: Phase 1 proposed linear regression. Evolved to K-Means clustering (3 clusters) to categorize over-provisioned vs balanced vs constrained instances and compute actionable monthly waste.
- GenAI Integration: Phase 1 used deprecated google-generativeai. Modernized to official google-genai SDK (gemini-3.8-flash) with Pydantic validation, application-controlled provenance, and deterministic offline rule fallback.

---

## Slide 8: Synthetic Multi-Cloud Dataset & Ingestion
*Realistic Multi-Provider Simulation with Isolated Ground-Truth Anomaly Corpus*

### Spoken Delivery Script
> "Slide 8 illustrates our data pipeline. To evaluate the platform rigorously without exposing proprietary corporate infrastructure or incurring cloud costs, we engineered a realistic multi-cloud generator. The active database contains 300 instances—AWS 155, Azure 88, and GCP 57—over a 90-day telemetry window, generating 27,000 daily metrics records. We injected 15 distinct ground-truth anomaly scenarios covering cpu_spike, brute_force, network_exfiltration, misconfiguration, and memory_leak; the model predicts 17 anomalies. Crucially, the ground-truth manifest was strictly held out and never accessed during feature extraction or inference, guaranteeing zero data leakage."

### Key Visual Bullets
- Fleet Diversity: 300 instances in the active database (AWS 155 / Azure 88 / GCP 57) spanning general, compute, and memory instance families.
- Telemetry Volume: 90 days of daily metrics (27,000 records) tracking CPU, RAM, Network In/Out, and Disk IOPS with diurnal patterns and stochastic noise.
- 15 Injected Anomaly Scenarios (5 Categories): cpu_spike (3), brute_force (3), network_exfiltration (3), misconfiguration (3), and memory_leak (3).
- Strict Evaluation Isolation: anomaly_manifest.json is stored separately and is NEVER accessed during feature engineering, training, or inference.

---

## Slide 9: Multi-Modal Anomaly Detection Engine
*11 Engineered Time-Series Features + Isolation Forest + Security Signals*

### Spoken Delivery Script
> "Cloud anomalies manifest across different time scales: sudden spikes occur in minutes, while memory leaks take weeks. Standard point-in-time metrics cannot detect these. Our multi-modal anomaly detector engineers 11 rolling time-series features, including median absolute deviation robust z-scores, rolling linear slopes for memory leaks, and cross-resource interaction terms. An Isolation Forest ensemble with 150 trees evaluates the feature matrix, producing a telemetry score that fuses with contextual security signals. Instances with a score of 65 or higher are flagged for operational triage."

### Key Visual Bullets
- 11 Rolling Features: Captures short-term shocks (robust z-score, day-to-day diff), medium-term drift (7-day vs 30-day dev), burstiness (peak-to-median net), and slow leaks (14-day rolling linear slope).
- Isolation Forest Architecture: 150 decision trees, contamination=0.05, random_state=42 (fixed for reproducibility, zero hardcoded rules).
- Multi-Modal Fusion: Combines calibrated telemetry score with contextual security signals (unpatched vulnerabilities, open ports, IAM level).
- Operational Decision: Instance flagged as an anomaly if combined score ≥ 65.0 (project-defined operational triage threshold, distinct from CVSS).

---

## Slide 10: FinOps Rightsizing & Cost Optimization
*Unsupervised K-Means Clustering for Fleet-Wide Cost Waste Identification*

### Spoken Delivery Script
> "For cloud cost optimization, CLARA applies unsupervised K-Means clustering across 30-day rolling CPU, memory, and cost metrics. The model partitions our 300 instances into three operational clusters: Cluster 0 represents over-provisioned or idle workloads; Cluster 1 represents healthy, balanced production instances; and Cluster 2 identifies resource-constrained instances running at over 84% utilization. Stored cost and rightsizing recommendations total $184.58 per month. Savings across all recommendation types total $220.87 per month."

### Key Visual Bullets
- Feature Dimensions: 30-day rolling average CPU, peak CPU, average memory utilization, and daily baseline cost.
- K-Means Clustering (k=3): Partitions fleet into Cluster 0 (Over-Provisioned/Idle), Cluster 1 (Balanced Workloads), and Cluster 2 (Constrained/High-Load).
- Actionable Waste Calculation: Waste = (1 - max(AvgCPU/50, AvgRAM/60)) * ProjectedMonthlySpend for over-provisioned instances.
- Recommendation Savings: $184.58/month from cost and rightsizing recommendations; $220.87/month across all recommendation types.
- Cluster 2 Insights: Identifies constrained instances operating at high utilization as candidates for proactive upsizing to prevent SLA violations.

---

## Slide 11: Composite Risk Formulation & Severity Tiers
*Unified Mathematical Weighting and Centralized Operational Classification*

### Spoken Delivery Script
> "To give operations teams a clear, unified triage priority, CLARA computes a Composite Risk Score weighting Security at 50%, Telemetry Anomaly at 30%, and Cost Waste at 20%. The formula is mathematically bounded between 0 and 100. We established centralized operational severity tiers: Critical for scores 80 and above, High for 60 to 80, Medium for 40 to 60, and Low for below 40. Under our semantic hardening, missing or invalid scores are explicitly classified as Unknown with neutral gray badges, ensuring that data pipeline errors are never misdiagnosed as low risk."

### Key Visual Bullets
- Composite Risk Formula: Overall Risk = (0.50 * Security Score) + (0.30 * Anomaly Score) + (0.20 * Cost Waste Score).
- Deterministic Security Posture: Scored (0-100) based on observable encryption, IAM, exposure, vulnerability-age and security-event indicators.
- Centralized Operational Tiers: Critical (≥ 80.0, red), High (60.0–79.9, orange), Medium (40.0–59.9, yellow), Low (0.0–39.9, green).
- Missing-Risk Semantics: NULL, NaN, non-numeric, or negative scores classified as UNKNOWN (slate gray), preventing silent misclassification as Low.

---

## Slide 12: Dual-Engine GenAI Advisory Architecture
*Modern Google GenAI SDK (gemini-3.8-flash) + Deterministic Offline Fallback*

### Spoken Delivery Script
> "Slide 12 showcases our dual-engine recommendation architecture. When triggered, the orchestrator triages candidate instances exhibiting high risk, anomalies, or waste. If a valid API key is present, it invokes Google Gemini using the modern google-genai SDK targeting gemini-3.8-flash. Responses are enforced via Pydantic schema validation and verified by an anti-hallucination guard that checks every instance ID against DuckDB. Crucially, provenance is application-controlled: the database records whether advice originated from Gemini or our deterministic rule engine. The pipeline remains operational in tested missing-key and API-failure scenarios by using our clearly labelled deterministic fallback engine."

### Key Visual Bullets
- Modern GenAI SDK: Integrates google-genai (gemini-3.8-flash endpoint) with structured system instructions.
- Strict Schema Validation: Enforces Pydantic RecommendationList contract (action title, category, priority, savings, justification, remediation steps).
- Anti-Hallucination Guard: Validates that returned instance IDs strictly exist in the triage candidate set; rejects fabricated IDs.
- Application-Controlled Provenance: Application code explicitly stamps generation_source, model_name, and fallback_reason into DuckDB.
- Operational Resilience: The pipeline remains operational in the tested missing-key and API-failure scenarios by using a clearly labelled deterministic fallback.

---

## Slide 13: Presentation Layer: Streamlit BI Dashboard
*Interactive Multi-Page Analytics with Dynamic Filtering and Provenance Badges*

### Spoken Delivery Script
> "Our user interface is an interactive four-page Streamlit business intelligence application. Page 1 provides executive-level visibility: KPI cards displaying actionable waste and active anomalies, with reactive cloud provider filters. Page 2 conducts deep security forensics across vulnerabilities, open ports, and IAM roles. Page 3 provides interactive FinOps rightsizing scatter plots and cost projections. And Page 4 displays our recommendation cards with clear provenance badges, technical justifications, and executable remediation playbooks."

### Key Visual Bullets
- Page 1: Executive Overview — Fleet KPI metric cards ($184.58 cost-recommendation savings, $220.87 all-recommendation savings, 1 critical, 6 high), multi-provider filters, risk distribution charts, and fleet inventory tables. The evaluation corpus contains 15 injected anomalies and the model predicts 17 instances at the operational threshold.
- Page 2: Security Analysis — Deep vulnerability breakdown, public ingress SSH/RDP analysis, wildcard IAM permissions, and posture distribution.
- Page 3: Cost Analysis — FinOps rightsizing scatter plots, spend vs waste trends, and downsizing recommendation tables.
- Page 4: AI Recommendations — Interactive recommendation cards with color-coded provenance badges ('Gemini 3.8 Flash' vs 'Deterministic Rule Fallback'), technical justifications, and remediation steps.

---

## Slide 14: Experimental Results & Model Evaluation
*Evaluation Against Ground-Truth Corpus Under Strict Data Isolation*

### Spoken Delivery Script
> "Slide 14 presents our quantitative evaluation results. Tested against our held-out seed-42 anomaly corpus, CLARA's production detector achieved 82.35% precision and 93.33% recall, surpassing both university acceptance thresholds of 80% and 85%, with an F1-score of 0.8750. The model detected 14 out of 15 injected anomalies with only 3 false positives out of 285 normal instances. In terms of category detection breadth, all five anomaly categories had at least one detected instance: brute_force, cpu_spike, network_exfiltration, and misconfiguration achieved 100% recall (3/3 each), while memory_leak achieved 66.7% recall (2/3). In addition, all 10 live Gemini recommendations achieved 100% Pydantic validation without a single hallucinated instance."

### Key Visual Bullets
- Evaluation Protocol: Evaluated on seed-42 corpus with anomaly_manifest.json completely held out during feature engineering, training, and threshold selection.
- Confusion Matrix: True Positives (TP) = 14, False Positives (FP) = 3, False Negatives (FN) = 1, True Negatives (TN) = 282.
- Quantitative Performance: Precision = 82.35% (exceeds ≥ 80% requirement), Recall = 93.33% (exceeds ≥ 85% requirement), F1-Score = 0.8750.
- Category Detection Breadth: All 5 anomaly categories had at least one detected instance:
-   • brute_force: 3/3 (100.0%)    • cpu_spike: 3/3 (100.0%)
-   • network_exfiltration: 3/3 (100.0%)    • misconfiguration: 3/3 (100.0%)
-   • memory_leak: 2/3 (66.7%)
- Gemini Verification: 10 live Gemini recommendations generated and verified in DuckDB; 100% schema conformance, zero hallucinated instances, immutable provenance.

---

## Slide 15: Automated Testing & Test Isolation
*Full Test Suite Passing, 67% Runtime-Package Coverage, Zero Production Data Mutation*

### Spoken Delivery Script
> "To guarantee software quality and continuous integration compatibility, we engineered a comprehensive automated test suite. A key engineering milestone was test isolation: our pytest fixtures use session-scoped temporary directories, ensuring that test runs never alter, overwrite, or delete the production clara.db database. The complete suite passes with 67% statement coverage across all runtime application packages. External Gemini calls are mocked, so tests require no API key, and our production database hash remains bit-for-bit unchanged."

### Key Visual Bullets
- Strict Test Isolation: Session-scoped pytest tmp_path fixtures create isolated DuckDB instances; root clara.db and CSVs are completely untouched.
- Full Test Suite: 75 unit, integration, and UI tests passing (100% pass rate).
- Verified Coverage: 67% statement coverage across all configured runtime packages, including data generation, warehousing, analytics, GenAI, and dashboard modules.
- Mocked External Dependencies: Tests execute offline without requiring internet access or live API keys; external Gemini calls mocked.
- Database Hash Preserved: Root production database verified bit-for-bit unchanged (SHA256: de271ea91da0df6c2a22c9d967684574fbd3f63fe25b6cab8a5c07c7b91f6bd8).

---

## Slide 16: Limitations & Ethical Governance
*Transparent Appraisal of Simulation Boundaries and Responsible AI Safeguards*

### Spoken Delivery Script
> "In accordance with academic rigor, we openly discuss our system limitations and ethical safeguards. First, while our synthetic generator is statistically realistic, live cloud environments have unpredictable edge cases like hypervisor reboots or transient network drops. Second, CLARA deliberately restricts itself to advisory decision support—autonomous write actions in enterprise infrastructure pose severe risk of accidental downtime. Third, external LLM latency necessitates relying on deterministic rules for sub-second real-time alerting. Ethically, we enforce zero credential exposure, transparent provenance labeling, and human-in-the-loop review."

### Key Visual Bullets
- Synthetic Simulation vs Live APIs: Synthetic telemetry models diurnal curves and stochastic noise accurately, but live clouds exhibit unpredictable edge cases (DNS throttling, hypervisor reboots).
- Advisory Scope: CLARA provides decision support; it deliberately does not execute autonomous IAM or instance modifications to avoid catastrophic service interruptions.
- API Latency: Gemini 3.8 Flash requires 1.5–3.5s per batch; real-time low-latency alerting relies on the deterministic rule engine.
- Responsible AI Governance: Zero credential exposure (keys stored in .env, never in repos or logs); immutable provenance transparency; human-in-the-loop review before any cloud remediation.

---

## Slide 17: Future Scope & Engineering Roadmap
*Planned Enhancements for Production Deployment and Closed-Loop Automation*

### Spoken Delivery Script
> "Looking forward, we have defined an engineering roadmap to transition CLARA from an academic prototype to enterprise production. First, we plan to implement read-only cloud connectors using AWS Boto3, Azure SDK, and GCP client libraries to ingest live metrics. Second, we aim to integrate Reinforcement Learning from Human Feedback, allowing operator interactions to fine-tune recommendation prompts. Third, we will integrate Infrastructure-as-Code pipelines, generating reviewable Terraform pull requests for approved rightsizing actions. And fourth, we will implement multi-tenant role-based access control and audit logging."

### Key Visual Bullets
- Live Cloud Connector Adapters: Implement read-only connectors via AWS Boto3, Azure SDK for Python, and GCP Client Libraries to stream live telemetry.
- Reinforcement Learning from Human Feedback (RLHF): Capture operator feedback (thumbs up/down, executed/dismissed) to dynamically tune prompts and risk weights.
- Infrastructure-as-Code (IaC) Integration: Automatically generate reviewable Terraform / Ansible pull requests for operator-approved downsizing or security patching.
- Multi-Tenant Role-Based Access Control (RBAC): Departmental quota enforcement, compliance audit logging, and SSO identity integration.

---

## Slide 18: Conclusion & Review Details
*Summary of Deliverables, Academic Review, and Open Q&A Session*

### Spoken Delivery Script
> "To conclude, CLARA demonstrates that pairing embedded analytical warehousing, explainable machine learning models, and structured Generative AI provides a practical, robust solution to the challenges of multi-cloud management. With verified 82.35% precision, 93.33% recall, a fully passing test suite, and honest 67% runtime-package coverage, our system is reproducible and ready for demonstration. We express our deepest gratitude to our project guide Dr. Geetabai Hukkeri and the faculty of MIT Bengaluru for their continuous support. Thank you very much. We now welcome questions and discussions from the committee."

### Key Visual Bullets
- CLARA successfully delivers an end-to-end, multi-cloud evaluation and risk assessment platform.
- Combines embedded DuckDB warehousing, 11-feature Isolation Forest anomaly detection, K-Means FinOps rightsizing, and modern Gemini 3.8 Flash recommendations.
- Evaluation Verified: 82.35% Precision, 93.33% Recall, full test suite passing, 67% runtime-package statement coverage.
- We express our sincere gratitude to Dr. Geetabai S Hukkeri, Dr. Rashmi R, and the Department of CSE, MIT Bengaluru.
- Thank you. We now invite questions, critiques, and feedback from the evaluators.

---
