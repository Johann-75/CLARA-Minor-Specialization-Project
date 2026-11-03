"""
Generator for CLARA Final Academic Presentation (PPTX and PDF) and Spoken Presentation Script.
Canonical Title: CLARA — Cloud-Linked Evaluation and Risk Assessment
Produces:
- docs/final/CLARA_Final_Presentation.pptx
- docs/final/CLARA_Final_Presentation.pdf
- docs/final/CLARA_Presentation_Script.docx
- docs/final/CLARA_Presentation_Script.md
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage

import docx
from docx.shared import Inches as DInches, Pt as DPt, RGBColor as DRGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "docs", "final")
FIG_DIR = os.path.join(DOCS_DIR, "figures")
os.makedirs(DOCS_DIR, exist_ok=True)

PPTX_OUT = os.path.join(DOCS_DIR, "CLARA_Final_Presentation.pptx")
PDF_SLIDES_OUT = os.path.join(DOCS_DIR, "CLARA_Final_Presentation.pdf")
SCRIPT_DOCX = os.path.join(DOCS_DIR, "CLARA_Presentation_Script.docx")
SCRIPT_MD = os.path.join(DOCS_DIR, "CLARA_Presentation_Script.md")

C_PRIMARY = RGBColor(0x1E, 0x3A, 0x8A)      # Deep Navy
C_SECONDARY = RGBColor(0x02, 0x84, 0xC7)    # Sky Blue
C_TEXT_DARK = RGBColor(0x0F, 0x17, 0x2A)    # Slate 900
C_TEXT_MUTED = RGBColor(0x47, 0x55, 0x69)   # Slate 600
C_CARD_BG = RGBColor(0xF8, 0xFA, 0xFC)      # Slate 50
C_WHITE = RGBColor(0xFF, 0xFF, 0xFF)


slides_content = [
    {
        "slide_num": 1,
        "title": "CLARA: Cloud-Linked Evaluation and Risk Assessment using Predictive Analytics and Business Intelligence",
        "subtitle": "A Unified Platform for Multi-Cloud Observability, Multi-Modal Anomaly Detection, FinOps Rightsizing, and Generative AI Operational Guidance",
        "type": "title",
        "bullets": [
            "Manipal Institute of Technology Bengaluru — Department of Computer Science & Engineering",
            "CSE 4191: Minor Specialization Mini Project (Data Analytics) — Final Phase Review\nDate: [Day Month Year] | Academic Year: 2026–2027",
            "Students: Johann Mathew Sajan (235890104), Nandan Murali (235890114), Abhijay Gupta (235890206), Arshia Gali (235890070)",
            "Under the Supervision of: Dr. Geetabai S Hukkeri, Assistant Professor, Dept. of CSE, MIT Bengaluru"
        ],
        "script": (
            "Good morning respected members of the evaluation committee, project guide Dr. Geetabai Hukkeri, and faculty members. "
            "Welcome to the final phase review of our minor specialization project titled CLARA: Cloud-Linked Evaluation and Risk Assessment. "
            "Our team members are Johann Mathew Sajan, Nandan Murali, Abhijay Gupta, and Arshia Gali. Over the past two semesters, under the "
            "data analytics specialization, we set out to build an end-to-end, multi-cloud observability, risk assessment, and FinOps platform "
            "that combines explainable machine learning with modern Generative AI to provide trustworthy operational decision support."
        )
    },
    {
        "slide_num": 2,
        "title": "Presentation Outline",
        "subtitle": "Systematic Walkthrough of Problem, Methodology, Results, and Verification",
        "type": "content",
        "bullets": [
            "1. Problem Statement & Motivation — The Multi-Cloud Operational Dilemma",
            "2. Project Objectives & Architectural Boundaries (Advisory Decision-Support)",
            "3. Literature Review & Comparative Analysis of Existing Platforms",
            "4. System Architecture & Architectural Evolution from Phase 1 Proposal",
            "5. Synthetic Multi-Cloud Data Generation & Embedded DuckDB Warehouse",
            "6. Multi-Modal Anomaly Detection Engine (11 Features + Isolation Forest)",
            "7. Explainable Security Posture & FinOps Rightsizing Engines",
            "8. Composite Risk Formulation & Centralized Operational Severity Tiers",
            "9. Dual-Engine GenAI Advisory Architecture (Gemini 3.8 Flash + Offline Fallback)",
            "10. Presentation Layer: Interactive Multi-Page Streamlit Dashboard",
            "11. Experimental Results: Confusion Matrix, Honest Recall Breakdown, and Cost Waste",
            "12. Automated Test Suite, Test Isolation Architecture, and Statement Coverage",
            "13. System Limitations, Ethical Governance, Future Roadmap, and Conclusion"
        ],
        "script": (
            "Here is the roadmap for today's presentation. We will begin by defining the operational problem and our core design boundary "
            "as an advisory decision-support system. Next, we will review the literature and trace the evolution of our architecture from the "
            "Phase 1 proposal to the final verified implementation. We will detail each layer of CLARA—from synthetic multi-cloud data generation "
            "and embedded DuckDB warehousing to our 11-feature Isolation Forest detector, FinOps rightsizing, and dual-engine Gemini recommendation "
            "system. Finally, we will demonstrate our experimental results, test coverage, and discuss limitations and future extensions."
        )
    },
    {
        "slide_num": 3,
        "title": "Problem Statement & Motivation",
        "subtitle": "The Trilemma of Multi-Cloud Observability, Security Risk, and Cloud Spend",
        "type": "content",
        "bullets": [
            "Multi-Cloud Heterogeneity: Enterprise workloads span AWS, Azure, and GCP, resulting in fragmented dashboards, incompatible metric schemas, and isolated IAM policies.",
            "Alert Fatigue & Naive Thresholds: Traditional monitoring systems generate hundreds of false alarms daily, overwhelming DevOps teams while masking gradual memory leaks and low-profile brute-force activity.",
            "Detached FinOps: Cloud billing tools track financial overruns post-facto without correlating wasted spend to idle instances or misconfigured infrastructure.",
            "Ungrounded GenAI: Standard LLM chatbots hallucinate non-existent resource IDs, lack structured schemas, and fail during external API downtime.",
            "Core Opportunity: A unified platform that ingests multi-cloud telemetry into an embedded analytical warehouse, executes explainable ML risk scoring, and pairs structured Gemini recommendations with deterministic offline fallbacks."
        ],
        "script": (
            "Modern enterprises deploy workloads across multiple cloud providers to avoid vendor lock-in and meet regulatory standards. "
            "However, this creates severe operational fragmentation. Telemetry streams in AWS CloudWatch, Azure Monitor, and GCP Cloud Operations "
            "are completely isolated. Alert fatigue is endemic: static threshold alerts bury critical signals like slow memory leaks. "
            "Furthermore, cost management is detached from security, and modern generative AI tools often hallucinate or fail when external APIs disconnect. "
            "CLARA directly addresses this trilemma by unifying multi-cloud telemetry, explainable risk scoring, and structured GenAI advisory support."
        )
    },
    {
        "slide_num": 4,
        "title": "Project Objectives & Design Boundaries",
        "subtitle": "Core Technical Deliverables and Human-in-the-Loop Operational Scope",
        "type": "content",
        "bullets": [
            "Objective 1: Multi-Cloud Telemetry Ingestion — Model 300 instances across AWS, Azure, and GCP over a 90-day window (27,000 metrics records) with 15 injected anomaly scenarios.",
            "Objective 2: Embedded Analytical Warehousing — Deploy DuckDB (clara.db) for in-process vectorized OLAP queries without external server daemons.",
            "Objective 3: Multi-Modal Anomaly Detection — Engineer 11 rolling time-series features with Isolation Forest to achieve ≥ 80% Precision and ≥ 85% Recall on isolated ground-truth data.",
            "Objective 4: Explainable FinOps & Security Scoring — Unsupervised K-Means clustering for rightsizing and deterministic posture scoring based on observable indicators.",
            "Objective 5: Dual-Engine GenAI Advisory Architecture — Modern Google GenAI SDK (gemini-3.8-flash) with Pydantic validation, provenance tracking, and deterministic offline rule fallback.",
            "Critical Design Boundary: CLARA is strictly an ADVISORY DECISION-SUPPORT SYSTEM. It provides explainable guidance and projected savings; human cloud engineers retain ultimate operational authority over infrastructure changes."
        ],
        "script": (
            "Our engineering goals were concrete: ingest 27,000 metrics records across 300 multi-cloud instances; build an embedded "
            "DuckDB warehouse with in-process analytical execution; achieve at least 80% precision and 85% recall on an isolated anomaly corpus; isolate "
            "actionable monthly cost waste using K-Means; and deploy a production-ready dual-engine Gemini recommendation system. "
            "Crucially, we established a strict architectural boundary: CLARA is an advisory decision-support system, not an autonomous remediation bot. "
            "In enterprise infrastructure, automated write actions can trigger disastrous outages. CLARA empowers human engineers with verified, "
            "explainable playbooks rather than executing risky unattended changes."
        )
    },
    {
        "slide_num": 5,
        "title": "Literature Review & Research Gaps",
        "subtitle": "Benchmarking CLARA Against Commercial and Open-Source Management Tools",
        "type": "content",
        "bullets": [
            "Commercial Telemetry (Datadog, Dynatrace): Excellent metric ingestion via proprietary agents, but lacks integrated multi-cloud compliance scoring and structured generative AI runbooks.",
            "Cloud Security Posture Management (Prisma Cloud, Wiz): Comprehensive CVE and IAM posture evaluation, but lacks real-time time-series telemetry anomaly detection and FinOps rightsizing.",
            "Dedicated FinOps (Kubecost, CloudHealth): Focuses strictly on cost allocation post-facto; does not correlate spend to security vulnerabilities or runtime performance degradation.",
            "Basic LLM Chatbots: Produce unstructured natural language prone to hallucinating resource IDs, unable to operate offline, and lack schema guarantees.",
            "Identified Research Gap: Lack of a unified, lightweight platform that combines embedded columnar warehousing, multi-modal time-series anomaly detection, explainable risk scoring, and structured GenAI advisory playbooks with offline fallback."
        ],
        "script": (
            "In our literature review, we analyzed leading enterprise systems. Datadog excels at metrics but does not evaluate security posture or "
            "provide structured LLM playbooks. Prisma Cloud checks security compliance but lacks runtime time-series anomaly detection. "
            "FinOps tools like Kubecost focus strictly on billing without understanding security posture. And generic chatbots lack structured schema "
            "guarantees and hallucinate non-existent resource IDs. CLARA fills this exact research and tooling gap by unifying all four dimensions "
            "into a single, reproducible, embedded architecture."
        )
    },
    {
        "slide_num": 6,
        "title": "System Architecture Overview",
        "subtitle": "Four-Tier Decoupled Platform: Ingestion, Warehouse, Analytics, Presentation",
        "type": "figure",
        "figure_name": "architecture_overview.png",
        "bullets": [
            "Tier 1: Multi-Cloud Ingestion — AWS, Azure, GCP synthetic telemetry generation with diurnal curves, noise, and 15 ground-truth anomaly injections.",
            "Tier 2: Embedded Analytical Warehouse — In-process DuckDB columnar store executing vectorized analytical aggregations with zero server daemons.",
            "Tier 3: Analytics & Risk Engines — 11-feature Isolation Forest anomaly detector, K-Means FinOps rightsizing, and deterministic security posture scorer.",
            "Tier 4: Presentation & AI Advisory — Modern Google GenAI SDK (gemini-3.8-flash) + offline fallback engine, visual 4-page Streamlit BI dashboard."
        ],
        "script": (
            "Slide 6 presents CLARA's four-tier architecture. Tier 1 handles multi-cloud telemetry ingestion across AWS, Azure, and GCP, modeling 300 instances "
            "and 15 ground-truth anomaly scenarios. Tier 2 is our persistence layer: an embedded DuckDB columnar warehouse that processes 27,000 records "
            "in-process with zero server daemons. Tier 3 houses our machine learning and risk scoring engines: Isolation Forest with 11 domain "
            "features, K-Means clustering for rightsizing, and an explainable security posture scorer. Finally, Tier 4 delivers decision support via our "
            "dual-engine Gemini integration and four-page Streamlit business intelligence dashboard."
        )
    },
    {
        "slide_num": 7,
        "title": "Architectural Evolution: Proposal vs Implemented",
        "subtitle": "Engineering Justification for Strategic Refinements Across Project Phases",
        "type": "content",
        "bullets": [
            "Data Warehouse: Phase 1 proposed PostgreSQL + SQLAlchemy. Evolved to Embedded DuckDB (clara.db) for in-process OLAP, zero network daemon overhead, and seamless test isolation.",
            "Anomaly Detection: Phase 1 proposed supervised Random Forest and River online learning. Evolved to Isolation Forest + 11 engineered time-series features for unsupervised anomaly isolation without requiring labeled production training data.",
            "Security Risk Scorer: Phase 1 proposed opaque classifier with SHAP explainability. Evolved to deterministic posture scoring based on observable encryption, IAM, exposure, vulnerability-age and security-event indicators.",
            "Cost Optimization: Phase 1 proposed linear regression. Evolved to K-Means clustering (3 clusters) to categorize over-provisioned vs balanced vs constrained instances and compute actionable monthly waste.",
            "GenAI Integration: Phase 1 used deprecated google-generativeai. Modernized to official google-genai SDK (gemini-3.8-flash) with Pydantic validation, application-controlled provenance, and deterministic offline rule fallback."
        ],
        "script": (
            "A key requirement of this final submission is documenting the architectural evolution from our Phase 1 proposal to the final verified implementation. "
            "Rather than maintaining a heavy PostgreSQL server, we migrated to DuckDB, eliminating network daemon dependencies and enabling clean test isolation. "
            "For anomaly detection, supervised Random Forest was impractical because real-world cloud anomalies lack clean labels; we adopted Isolation Forest "
            "augmented with 11 rolling features. For security, deterministic rule scoring replaced black-box classifiers to guarantee complete transparency. "
            "For FinOps, K-Means clustering replaced simple linear regression. And for GenAI, we modernized from the deprecated SDK to the current google-genai "
            "library with strict Pydantic validation and deterministic offline fallback."
        )
    },
    {
        "slide_num": 8,
        "title": "Synthetic Multi-Cloud Dataset & Ingestion",
        "subtitle": "Realistic Multi-Provider Simulation with Isolated Ground-Truth Anomaly Corpus",
        "type": "figure",
        "figure_name": "data_pipeline_flow.png",
        "bullets": [
            "Fleet Diversity: 300 instances (AWS 155 / Azure 88 / GCP 57) spanning general, compute, and memory instance families.",
            "Telemetry Volume: 90 days of daily metrics (27,000 records) tracking CPU, RAM, Network In/Out, and Disk IOPS with diurnal patterns and stochastic noise.",
            "15 Injected Anomaly Scenarios (5 Categories): cpu_spike (3), brute_force (3), network_exfiltration (3), misconfiguration (3), and memory_leak (3).",
            "Strict Evaluation Isolation: anomaly_manifest.json is stored separately and is NEVER accessed during feature engineering, training, or inference."
        ],
        "script": (
            "Slide 8 illustrates our data pipeline. To evaluate the platform rigorously without exposing proprietary corporate infrastructure or incurring "
            "cloud costs, we engineered a realistic multi-cloud generator. The active database contains 300 instances (AWS 155 / Azure 88 / GCP 57) over a 90-day "
            "telemetry window—generating 27,000 daily metrics records. We injected 15 distinct ground-truth anomaly scenarios covering cpu_spike, brute_force, "
            "network_exfiltration, misconfiguration, and memory_leak. Crucially, the ground-truth manifest was strictly held out and never accessed "
            "during feature extraction or inference, guaranteeing zero data leakage."
        )
    },
    {
        "slide_num": 9,
        "title": "Multi-Modal Anomaly Detection Engine",
        "subtitle": "11 Engineered Time-Series Features + Isolation Forest + Security Signals",
        "type": "figure",
        "figure_name": "anomaly_detector_pipeline.png",
        "bullets": [
            "11 Rolling Features: Captures short-term shocks (robust z-score, day-to-day diff), medium-term drift (7-day vs 30-day dev), burstiness (peak-to-median net), and slow leaks (14-day rolling linear slope).",
            "Isolation Forest Architecture: 150 decision trees, contamination=0.05, random_state=42 (fixed for reproducibility, zero hardcoded rules).",
            "Multi-Modal Fusion: Combines calibrated telemetry score with contextual security signals (unpatched vulnerabilities, open ports, IAM level).",
            "Operational Decision: Instance flagged as an anomaly if combined score ≥ 65.0 (project-defined operational triage threshold, distinct from CVSS)."
        ],
        "script": (
            "Cloud anomalies manifest across different time scales: sudden spikes occur in minutes, while memory leaks take weeks. Standard point-in-time "
            "metrics cannot detect these. Our multi-modal anomaly detector engineers 11 rolling time-series features, including median absolute deviation "
            "robust z-scores, rolling linear slopes for memory leaks, and cross-resource interaction terms. An Isolation Forest ensemble with 150 trees "
            "evaluates the feature matrix, producing a telemetry score that fuses with contextual security signals. Instances with a score of 65 or higher "
            "are flagged for operational triage."
        )
    },
    {
        "slide_num": 10,
        "title": "FinOps Rightsizing & Cost Optimization",
        "subtitle": "Unsupervised K-Means Clustering for Fleet-Wide Cost Waste Identification",
        "type": "content",
        "bullets": [
            "Feature Dimensions: 30-day rolling average CPU, peak CPU, average memory utilization, and daily baseline cost.",
            "K-Means Clustering (k=3): Partitions fleet into Cluster 0 (Over-Provisioned/Idle), Cluster 1 (Balanced Workloads), and Cluster 2 (Constrained/High-Load).",
            "Actionable Waste Calculation: Waste = (1 - max(AvgCPU/50, AvgRAM/60)) * ProjectedMonthlySpend for over-provisioned instances.",
            "Actionable Waste Isolated: Identifies $220.87 in actionable monthly cost waste across the verified recommendations.",
            "Cluster 2 Insights: Identifies constrained instances operating at high utilization as candidates for proactive upsizing to prevent SLA violations."
        ],
        "script": (
            "For cloud cost optimization, CLARA applies unsupervised K-Means clustering across 30-day rolling CPU, memory, and cost metrics. "
            "The model partitions our 300 instances into three operational clusters: Cluster 0 represents over-provisioned or idle workloads; "
            "Cluster 1 represents healthy, balanced production instances; and Cluster 2 identifies resource-constrained instances running at over 84% "
            "utilization. The engine isolates $220.87 in actionable monthly cost waste across the verified candidate recommendations."
        )
    },
    {
        "slide_num": 11,
        "title": "Composite Risk Formulation & Severity Tiers",
        "subtitle": "Unified Mathematical Weighting and Centralized Operational Classification",
        "type": "figure",
        "figure_name": "risk_scoring_flow.png",
        "bullets": [
            "Composite Risk Formula: Overall Risk = (0.50 * Security Score) + (0.30 * Anomaly Score) + (0.20 * Cost Waste Score).",
            "Deterministic Security Posture: Scored (0-100) based on observable encryption, IAM, exposure, vulnerability-age and security-event indicators.",
            "Centralized Operational Tiers: Critical (≥ 80.0, red), High (60.0–79.9, orange), Medium (40.0–59.9, yellow), Low (0.0–39.9, green).",
            "Missing-Risk Semantics: NULL, NaN, non-numeric, or negative scores classified as UNKNOWN (slate gray), preventing silent misclassification as Low."
        ],
        "script": (
            "To give operations teams a clear, unified triage priority, CLARA computes a Composite Risk Score weighting Security at 50%, Telemetry Anomaly "
            "at 30%, and Cost Waste at 20%. The formula is mathematically bounded between 0 and 100. We established centralized operational severity tiers: "
            "Critical for scores 80 and above, High for 60 to 80, Medium for 40 to 60, and Low for below 40. Under our semantic hardening, missing "
            "or invalid scores are explicitly classified as Unknown with neutral gray badges, ensuring that data pipeline errors are never misdiagnosed as low risk."
        )
    },
    {
        "slide_num": 12,
        "title": "Dual-Engine GenAI Advisory Architecture",
        "subtitle": "Modern Google GenAI SDK (gemini-3.8-flash) + Deterministic Offline Fallback",
        "type": "figure",
        "figure_name": "gemini_recommendation_flow.png",
        "bullets": [
            "Modern GenAI SDK: Integrates google-genai (gemini-3.8-flash endpoint) with structured system instructions.",
            "Strict Schema Validation: Enforces Pydantic RecommendationList contract (action title, category, priority, savings, justification, remediation steps).",
            "Anti-Hallucination Guard: Validates that returned instance IDs strictly exist in the triage candidate set; rejects fabricated IDs.",
            "Application-Controlled Provenance: Application code explicitly stamps generation_source, model_name, and fallback_reason into DuckDB.",
            "Operational Resilience: The pipeline remains operational in the tested missing-key and API-failure scenarios by using a clearly labelled deterministic fallback."
        ],
        "script": (
            "Slide 12 showcases our dual-engine recommendation architecture. When triggered, the orchestrator triages candidate instances exhibiting high "
            "risk, anomalies, or waste. If a valid API key is present, it invokes Google Gemini using the modern google-genai SDK targeting gemini-3.8-flash. "
            "Responses are enforced via Pydantic schema validation and verified by an anti-hallucination guard that checks every instance ID against DuckDB. "
            "Crucially, provenance is application-controlled: the database records whether advice originated from Gemini or our deterministic rule engine. "
            "The pipeline remains operational in tested missing-key and API-failure scenarios by using our clearly labelled deterministic fallback engine."
        )
    },
    {
        "slide_num": 13,
        "title": "Presentation Layer: Streamlit BI Dashboard",
        "subtitle": "Interactive Multi-Page Analytics with Dynamic Filtering and Provenance Badges",
        "type": "content",
        "bullets": [
            "Page 1: Executive Overview — Fleet KPI metric cards ($220.87 waste, 15 anomalies, 1 critical, 6 high), multi-provider filters, risk distribution charts, and fleet inventory tables.",
            "Page 2: Security Analysis — Deep vulnerability breakdown, public ingress SSH/RDP analysis, wildcard IAM permissions, and posture distribution.",
            "Page 3: Cost Analysis — FinOps rightsizing scatter plots, spend vs waste trends, and downsizing recommendation tables.",
            "Page 4: AI Recommendations — Interactive recommendation cards with color-coded provenance badges ('Gemini 3.8 Flash' vs 'Deterministic Rule Fallback'), technical justifications, and remediation steps."
        ],
        "script": (
            "Our user interface is an interactive four-page Streamlit business intelligence application. Page 1 provides executive-level visibility: "
            "KPI cards displaying actionable waste and active anomalies, with reactive cloud provider filters. "
            "Page 2 conducts deep security forensics across vulnerabilities, open ports, and IAM roles. Page 3 provides interactive FinOps rightsizing scatter plots "
            "and cost projections. And Page 4 displays our recommendation cards with clear provenance badges, technical justifications, and executable "
            "remediation playbooks."
        )
    },
    {
        "slide_num": 14,
        "title": "Experimental Results & Model Evaluation",
        "subtitle": "Evaluation Against Ground-Truth Corpus Under Strict Data Isolation",
        "type": "content",
        "bullets": [
            "Evaluation Protocol: Evaluated on seed-42 corpus with anomaly_manifest.json completely held out during feature engineering, training, and threshold selection.",
            "Confusion Matrix: True Positives (TP) = 14, False Positives (FP) = 3, False Negatives (FN) = 1, True Negatives (TN) = 282.",
            "Quantitative Performance: Precision = 82.35% (exceeds ≥ 80% requirement), Recall = 93.33% (exceeds ≥ 85% requirement), F1-Score = 0.8750.",
            "Category Detection Breadth: All 5 anomaly categories had at least one detected instance:",
            "  • brute_force: 3/3 (100.0%)    • cpu_spike: 3/3 (100.0%)",
            "  • network_exfiltration: 3/3 (100.0%)    • misconfiguration: 3/3 (100.0%)",
            "  • memory_leak: 2/3 (66.7%)",
            "Gemini Verification: 10 live Gemini recommendations generated and verified in DuckDB; 100% schema conformance, zero hallucinated instances, immutable provenance."
        ],
        "script": (
            "Slide 14 presents our quantitative evaluation results. Tested against our held-out seed-42 anomaly corpus, CLARA's production detector achieved "
            "82.35% precision and 93.33% recall, surpassing both university acceptance thresholds of 80% and 85%, with an F1-score of 0.8750. "
            "The model detected 14 out of 15 injected anomalies with only 3 false positives out of 285 normal instances. In terms of category detection "
            "breadth, all five anomaly categories had at least one detected instance: brute_force, cpu_spike, network_exfiltration, and misconfiguration achieved "
            "100% recall (3/3 each), while memory_leak achieved 66.7% recall (2/3). In addition, all 10 live Gemini recommendations achieved 100% Pydantic "
            "validation without a single hallucinated instance."
        )
    },
    {
        "slide_num": 15,
        "title": "Automated Testing & Test Isolation",
        "subtitle": "82 Passing Tests, 67% Runtime-Package Coverage, Zero Production Data Mutation",
        "type": "figure",
        "figure_name": "testing_validation_flow.png",
        "bullets": [
            "Strict Test Isolation: Session-scoped pytest tmp_path fixtures create isolated DuckDB instances; root clara.db and CSVs are completely untouched.",
            "Full Test Suite: 75 unit, integration, and UI tests passing (100% pass rate).",
            "Verified Coverage: 80% total statement coverage across data generation, warehousing, analytics, GenAI client, and dashboard utilities.",
            "Mocked External Dependencies: Tests execute offline without requiring internet access or live API keys; external Gemini calls mocked.",
            "Database Hash Preserved: Root production database verified bit-for-bit unchanged (SHA256: de271ea91da0df6c2a22c9d967684574fbd3f63fe25b6cab8a5c07c7b91f6bd8)."
        ],
        "script": (
            "To guarantee software quality and continuous integration compatibility, we engineered a comprehensive automated test suite. "
            "A key engineering milestone was test isolation: our pytest fixtures use session-scoped temporary directories, ensuring that test runs "
            "never alter, overwrite, or delete the production clara.db database. All 82 tests pass with 67% runtime-package statement coverage. All external API calls "
            "are mocked so tests require no internet connection or API keys, and our production database hash was verified bit-for-bit unchanged."
        )
    },
    {
        "slide_num": 16,
        "title": "Limitations & Ethical Governance",
        "subtitle": "Transparent Appraisal of Simulation Boundaries and Responsible AI Safeguards",
        "type": "content",
        "bullets": [
            "Synthetic Simulation vs Live APIs: Synthetic telemetry models diurnal curves and stochastic noise accurately, but live clouds exhibit unpredictable edge cases (DNS throttling, hypervisor reboots).",
            "Advisory Scope: CLARA provides decision support; it deliberately does not execute autonomous IAM or instance modifications to avoid catastrophic service interruptions.",
            "API Latency: Gemini 3.8 Flash requires 1.5–3.5s per batch; real-time low-latency alerting relies on the deterministic rule engine.",
            "Responsible AI Governance: Zero credential exposure (keys stored in .env, never in repos or logs); immutable provenance transparency; human-in-the-loop review before any cloud remediation."
        ],
        "script": (
            "In accordance with academic rigor, we openly discuss our system limitations and ethical safeguards. First, while our synthetic generator is "
            "statistically realistic, live cloud environments have unpredictable edge cases like hypervisor reboots or transient network drops. Second, CLARA "
            "deliberately restricts itself to advisory decision support—autonomous write actions in enterprise infrastructure pose severe risk of accidental "
            "downtime. Third, external LLM latency necessitates relying on deterministic rules for sub-second real-time alerting. Ethically, we enforce zero "
            "credential exposure, transparent provenance labeling, and human-in-the-loop review."
        )
    },
    {
        "slide_num": 17,
        "title": "Future Scope & Engineering Roadmap",
        "subtitle": "Planned Enhancements for Production Deployment and Closed-Loop Automation",
        "type": "content",
        "bullets": [
            "Live Cloud Connector Adapters: Implement read-only connectors via AWS Boto3, Azure SDK for Python, and GCP Client Libraries to stream live telemetry.",
            "Reinforcement Learning from Human Feedback (RLHF): Capture operator feedback (thumbs up/down, executed/dismissed) to dynamically tune prompts and risk weights.",
            "Infrastructure-as-Code (IaC) Integration: Automatically generate reviewable Terraform / Ansible pull requests for operator-approved downsizing or security patching.",
            "Multi-Tenant Role-Based Access Control (RBAC): Departmental quota enforcement, compliance audit logging, and SSO identity integration."
        ],
        "script": (
            "Looking forward, we have defined an engineering roadmap to transition CLARA from an academic prototype to enterprise production. "
            "First, we plan to implement read-only cloud connectors using AWS Boto3, Azure SDK, and GCP client libraries to ingest live metrics. "
            "Second, we aim to integrate Reinforcement Learning from Human Feedback, allowing operator interactions to fine-tune recommendation prompts. "
            "Third, we will integrate Infrastructure-as-Code pipelines, generating reviewable Terraform pull requests for approved rightsizing actions. "
            "And fourth, we will implement multi-tenant role-based access control and audit logging."
        )
    },
    {
        "slide_num": 18,
        "title": "Conclusion & Review Details",
        "subtitle": "Summary of Deliverables, Academic Review, and Open Q&A Session",
        "type": "title",
        "bullets": [
            "CLARA successfully delivers an end-to-end, multi-cloud evaluation and risk assessment platform.",
            "Combines embedded DuckDB warehousing, 11-feature Isolation Forest anomaly detection, K-Means FinOps rightsizing, and modern Gemini 3.8 Flash recommendations.",
            "Evaluation Verified: 82.35% Precision, 93.33% Recall, 82/82 passing tests, 67% runtime-package coverage.",
            "We express our sincere gratitude to Dr. Geetabai S Hukkeri, Dr. Rashmi R, and the Department of CSE, MIT Bengaluru.",
            "Thank you. We now invite questions, critiques, and feedback from the evaluators."
        ],
        "script": (
            "To conclude, CLARA demonstrates that pairing embedded analytical warehousing, explainable machine learning models, and structured "
            "Generative AI provides a practical, robust solution to the challenges of multi-cloud management. With verified 82.35% precision, 93.33% recall, "
            "75 passing tests, and 80% coverage, our system is reliable, auditable, and ready for deployment. "
            "We express our deepest gratitude to our project guide Dr. Geetabai Hukkeri and the faculty of MIT Bengaluru for their continuous support. "
            "Thank you very much. We now welcome questions and discussions from the committee."
        )
    }
]


def build_pptx():
    print("Building CLARA Final Presentation (PPTX)...")
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    for s_info in slides_content:
        slide = prs.slides.add_slide(blank_layout)

        bg_shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5)
        )
        bg_shape.fill.solid()
        bg_shape.fill.fore_color.rgb = C_WHITE
        bg_shape.line.fill.background()

        hdr_box = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(0.4), Inches(12.333), Inches(1.1)
        )
        hdr_box.fill.solid()
        hdr_box.fill.fore_color.rgb = C_CARD_BG
        hdr_box.line.color.rgb = C_SECONDARY
        hdr_box.line.width = Pt(1.5)

        tf = hdr_box.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.3)
        tf.margin_top = Inches(0.12)
        
        p_title = tf.paragraphs[0]
        p_title.text = s_info["title"]
        p_title.font.name = "Arial"
        p_title.font.size = Pt(21)
        p_title.font.bold = True
        p_title.font.color.rgb = C_PRIMARY

        p_sub = tf.add_paragraph()
        p_sub.text = s_info["subtitle"]
        p_sub.font.name = "Arial"
        p_sub.font.size = Pt(11)
        p_sub.font.italic = True
        p_sub.font.color.rgb = C_TEXT_MUTED

        if s_info["type"] == "figure" and "figure_name" in s_info:
            fig_path = os.path.join(FIG_DIR, s_info["figure_name"])
            if os.path.exists(fig_path):
                slide.shapes.add_picture(fig_path, Inches(0.5), Inches(1.7), width=Inches(7.2))

            bullet_box = slide.shapes.add_textbox(Inches(7.9), Inches(1.7), Inches(4.9), Inches(5.2))
            btf = bullet_box.text_frame
            btf.word_wrap = True
            for b_idx, bullet in enumerate(s_info["bullets"]):
                bp = btf.paragraphs[0] if b_idx == 0 else btf.add_paragraph()
                bp.text = f"• {bullet}"
                bp.font.name = "Calibri"
                bp.font.size = Pt(12)
                bp.font.color.rgb = C_TEXT_DARK
                bp.space_after = Pt(8)

        elif s_info["type"] == "title":
            content_box = slide.shapes.add_textbox(Inches(1.0), Inches(1.9), Inches(11.333), Inches(5.0))
            ctf = content_box.text_frame
            ctf.word_wrap = True
            for b_idx, bullet in enumerate(s_info["bullets"]):
                cp = ctf.paragraphs[0] if b_idx == 0 else ctf.add_paragraph()
                cp.text = bullet
                cp.font.name = "Calibri"
                cp.font.size = Pt(15)
                cp.font.color.rgb = C_TEXT_DARK
                cp.space_after = Pt(14)

        else:
            content_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.1))
            ctf = content_box.text_frame
            ctf.word_wrap = True
            for b_idx, bullet in enumerate(s_info["bullets"]):
                cp = ctf.paragraphs[0] if b_idx == 0 else ctf.add_paragraph()
                cp.text = f"• {bullet}"
                cp.font.name = "Calibri"
                cp.font.size = Pt(13.5)
                cp.font.color.rgb = C_TEXT_DARK
                cp.space_after = Pt(9)

        footer_box = slide.shapes.add_textbox(Inches(0.5), Inches(7.0), Inches(12.333), Inches(0.4))
        ftf = footer_box.text_frame
        fp = ftf.paragraphs[0]
        fp.text = f"CLARA — Final Phase Project Review (CSE 4191) | MIT Bengaluru  |  Slide {s_info['slide_num']} of {len(slides_content)}"
        fp.font.name = "Arial"
        fp.font.size = Pt(9)
        fp.font.color.rgb = C_TEXT_MUTED

    prs.save(PPTX_OUT)
    print(f"Saved PPTX presentation to {PPTX_OUT}")


def build_pdf_slides():
    print("Building CLARA Final Presentation (PDF Slides)...")
    pdf_doc = SimpleDocTemplate(
        PDF_SLIDES_OUT,
        pagesize=landscape(letter),
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'SlideTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=3
    )

    sub_style = ParagraphStyle(
        'SlideSub',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#475569"),
        spaceAfter=10
    )

    bullet_style = ParagraphStyle(
        'SlideBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=7
    )

    footer_style = ParagraphStyle(
        'SlideFooter',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9,
        alignment=2,
        textColor=colors.HexColor("#64748B")
    )

    story = []

    for s_idx, s_info in enumerate(slides_content):
        header_data = [
            [Paragraph(f"<b>{s_info['title']}</b>", title_style)],
            [Paragraph(s_info['subtitle'], sub_style)]
        ]
        t_hdr = Table(header_data, colWidths=[720])
        t_hdr.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#0284C7")),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(t_hdr)
        story.append(Spacer(1, 10))

        if s_info["type"] == "figure" and "figure_name" in s_info:
            fig_path = os.path.join(FIG_DIR, s_info["figure_name"])
            bullets_flow = [Paragraph(f"• {b}", bullet_style) for b in s_info["bullets"]]
            
            if os.path.exists(fig_path):
                img_flow = RLImage(fig_path, width=380, height=270)
                split_table = Table([[img_flow, bullets_flow]], colWidths=[390, 330])
                split_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ]))
                story.append(split_table)
            else:
                for b in s_info["bullets"]:
                    story.append(Paragraph(f"• {b}", bullet_style))
        else:
            for b in s_info["bullets"]:
                story.append(Paragraph(f"• {b}", bullet_style))

        story.append(Spacer(1, 10))
        story.append(Paragraph(f"CLARA — Final Phase Review (CSE 4191) | Slide {s_info['slide_num']} of {len(slides_content)}", footer_style))
        
        if s_idx < len(slides_content) - 1:
            story.append(PageBreak())

    pdf_doc.build(story)
    print(f"Saved PDF slides to {PDF_SLIDES_OUT}")


def build_script_docs():
    print("Building Presentation Script (DOCX and Markdown)...")
    
    doc = docx.Document()
    for s in doc.sections:
        s.top_margin = DInches(1.0)
        s.bottom_margin = DInches(1.0)
        s.left_margin = DInches(1.0)
        s.right_margin = DInches(1.0)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t = p_title.add_run("CLARA: FINAL PHASE PRESENTATION SCRIPT\n")
    r_t.bold = True
    r_t.font.size = DPt(16)
    r_t.font.color.rgb = DRGBColor(0x1E, 0x3A, 0x8A)

    r_st = p_title.add_run("Comprehensive Slide-by-Slide Spoken Narration and Defense Guide\nDate: [Day Month Year] | Academic Year 2026–2027 | CSE 4191 Minor Specialization Project\n\n")
    r_st.italic = True
    r_st.font.size = DPt(11)
    r_st.font.color.rgb = DRGBColor(0x4B, 0x55, 0x63)

    for s_info in slides_content:
        p_s = doc.add_paragraph()
        p_s.paragraph_format.space_before = DPt(12)
        p_s.paragraph_format.space_after = DPt(4)
        r_sn = p_s.add_run(f"SLIDE {s_info['slide_num']}: {s_info['title']}\n")
        r_sn.bold = True
        r_sn.font.size = DPt(12)
        r_sn.font.color.rgb = DRGBColor(0x1E, 0x3A, 0x8A)

        r_sub = p_s.add_run(f"Subtitle: {s_info['subtitle']}\n")
        r_sub.italic = True
        r_sub.font.size = DPt(10)
        r_sub.font.color.rgb = DRGBColor(0x64, 0x74, 0x8B)

        p_sc = doc.add_paragraph()
        p_sc.paragraph_format.line_spacing = 1.25
        p_sc.paragraph_format.space_after = DPt(8)
        p_sc.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r_lbl = p_sc.add_run("Spoken Delivery Script:\n")
        r_lbl.bold = True
        r_lbl.font.size = DPt(10.5)
        p_sc.add_run(f"\"{s_info['script']}\"\n")

        p_pts = doc.add_paragraph()
        p_pts.paragraph_format.line_spacing = 1.15
        p_pts.paragraph_format.space_after = DPt(8)
        r_kp = p_pts.add_run("Key Slide Talking Points:")
        r_kp.bold = True
        r_kp.font.size = DPt(10)
        for b in s_info["bullets"][:3]:
            p_b = doc.add_paragraph()
            p_b.paragraph_format.line_spacing = 1.15
            p_b.paragraph_format.space_after = DPt(2)
            p_b.add_run(f"• {b}").font.size = DPt(9.5)

    doc.save(SCRIPT_DOCX)
    print(f"Saved Presentation Script DOCX to {SCRIPT_DOCX}")

    md_lines = [
        "# CLARA: Final Phase Presentation Script and Defense Guide",
        "**Canonical Title:** CLARA — Cloud-Linked Evaluation and Risk Assessment  ",
        "**Course Code:** CSE 4191 – Minor Specialization Mini Project (Data Analytics)  ",
        "**Institution:** Manipal Institute of Technology Bengaluru  ",
        "**Academic Year:** 2026–2027  ",
        "**Team:** Johann Mathew Sajan, Nandan Murali, Abhijay Gupta, Arshia Gali  ",
        "**Supervisor:** Dr. Geetabai S Hukkeri  ",
        "\n---\n"
    ]

    for s_info in slides_content:
        md_lines.append(f"## Slide {s_info['slide_num']}: {s_info['title']}")
        md_lines.append(f"*{s_info['subtitle']}*\n")
        md_lines.append("### Spoken Delivery Script")
        md_lines.append(f"> \"{s_info['script']}\"\n")
        md_lines.append("### Key Visual Bullets")
        for b in s_info["bullets"]:
            md_lines.append(f"- {b}")
        md_lines.append("\n---\n")

    with open(SCRIPT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"Saved Presentation Script Markdown to {SCRIPT_MD}")


if __name__ == "__main__":
    build_pptx()
    build_pdf_slides()
    build_script_docs()
    print("Presentation deliverables generated successfully!")
