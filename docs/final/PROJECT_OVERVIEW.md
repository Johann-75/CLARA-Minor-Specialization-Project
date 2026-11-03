# CLARA: Cloud-Linked Evaluation and Risk Assessment
## Executive Technical Project Overview

**Academic Program:** Bachelor of Technology in Computer Science & Engineering  
**Course Code:** CSE 4191 – Minor Specialization Mini Project (Data Analytics)  
**Academic Year:** 2026 – 2027  
**Institution:** Manipal Institute of Technology Bengaluru  
**Student Team:** Johann Mathew Sajan (235890104), Nandan Murali (235890114), Abhijay Gupta (235890206), Arshia Gali (235890070)  
**Project Guide:** Dr. Geetabai S Hukkeri, Assistant Professor, Dept. of CSE, MIT Bengaluru  
**Minor Specialization Coordinator:** Dr. Rashmi R, Assistant Professor  

---

## 1. Executive Summary

**CLARA (Cloud-Linked Evaluation and Risk Assessment)** is an advisory decision-support platform designed for unified multi-cloud observability, multi-modal anomaly detection, explainable security risk scoring, FinOps cost rightsizing, and Generative AI operational recommendations. 

Modern enterprise workloads routinely span Amazon Web Services (AWS), Microsoft Azure, and Google Cloud Platform (GCP). However, operations teams face acute domain fragmentation: telemetry data is siloed across vendor-specific dashboards, security posture signals are evaluated in isolation from runtime performance, and FinOps billing tools track cost overruns post-facto. Static threshold alerts generate rampant alert fatigue, and generic LLM chatbots hallucinate resource IDs while failing during network partitions.

CLARA resolves these challenges through a unified four-tier architecture:
1. **Multi-Cloud Synthetic Telemetry Engine:** The active database contains 300 instances (AWS 155 / Azure 88 / GCP 57) over a 90-day monitoring window (27,000 metrics records), featuring 15 injected ground-truth anomaly scenarios spanning 5 operational categories (`cpu_spike`, `brute_force`, `network_exfiltration`, `misconfiguration`, `memory_leak`).
2. **Embedded Analytical Warehouse (DuckDB):** In-process columnar database providing vectorized OLAP aggregations across telemetry, costs, vulnerabilities, and ML scores without external server daemons.
3. **Multi-Modal Anomaly Detection:** Isolation Forest ensemble augmented with 11 domain-engineered rolling time-series features (robust z-scores, rolling linear slopes, peak-to-median ratios) and contextual security signals. Achieves **82.35% Precision, 93.33% Recall, and 0.8750 F1-score** on an isolated evaluation corpus. Category detection breadth: all 5 anomaly categories had at least one detected instance.
4. **FinOps Rightsizing Engine:** Unsupervised K-Means clustering supports **$184.58/month in cost and rightsizing recommendations**. Savings across all recommendation types total **$220.87/month**.
5. **Deterministic Security & Composite Risk Scoring:** Deterministic, explainable posture scoring based on observable encryption, IAM, exposure, vulnerability-age and security-event indicators; synthesized via a tri-factor formula (50% Security, 30% Anomaly, 20% Cost Waste) into centralized operational severity tiers (Critical, High, Medium, Low, Unknown).
6. **Dual-Engine GenAI Advisory Architecture:** Modern Google GenAI SDK (`gemini-3.8-flash`) with structured Pydantic schema validation, anti-hallucination instance verification, and immutable application-controlled provenance. The pipeline remains operational in tested missing-key and API-failure scenarios by using a clearly labelled deterministic fallback.
7. **Interactive BI Dashboard:** Responsive four-page Streamlit application delivering executive KPI summaries, security forensics, FinOps scatter plots, and AI recommendation playbooks.
8. **Automated Quality Verification:** The full test suite passes with **67% statement coverage across all runtime packages** under strict session-scoped temporary database isolation.

---

## 2. Key Architecture Pillars

| Architectural Layer | Core Technology | Primary Functionality | Quantified Outcome |
| :--- | :--- | :--- | :--- |
| **Ingestion Layer** | Python Multi-Cloud Generator | Simulates AWS EC2, Azure VM, GCP Compute Engine workloads with diurnal trends and 15 ground-truth anomaly injections. | 300 instances (AWS 155 / Azure 88 / GCP 57), 27,000 daily metrics, 15 injected anomalies across 5 categories. |
| **Persistence Layer** | Embedded DuckDB (`clara.db`) | In-process columnar OLAP warehouse with normalized relational tables, analytical views, and zero external daemon dependencies. | In-process vectorized aggregations; zero network port overhead. |
| **Anomaly Engine** | Isolation Forest + 11 Time-Series Features | Evaluates rolling robust z-scores, rolling slopes, peak ratios, and security context; operational triage threshold = 65.0. | Precision: 82.35%, Recall: 93.33%, F1: 0.8750; all 5 anomaly categories detected. |
| **FinOps Engine** | K-Means Clustering (k=3) | Unsupervised partitioning into Over-Provisioned/Idle, Balanced, and Constrained instances; calculates rightsizing opportunities. | $184.58 cost-recommendation savings; $220.87 savings across all recommendation types. |
| **Security Engine** | Deterministic Posture Scorer | Scored on observable encryption, IAM, exposure, vulnerability-age and security-event indicators. | Bounded [0.0, 100.0] score; 1 Critical, 6 High risk instances in fleet. |
| **Composite Risk** | Multi-Factor Formulation | Tri-factor weighting: `0.5*Security + 0.3*Anomaly + 0.2*CostWaste`; centralized tiers: Critical, High, Medium, Low, Unknown. | Centralized severity semantics; missing data classified as UNKNOWN (gray). |
| **GenAI Engine** | Google GenAI SDK (`gemini-3.8-flash`) + Offline Rules | Structured Pydantic contract validation, anti-hallucination candidate validation, application-controlled provenance, offline fallback. | 10 verified live Gemini records in DuckDB; 100% schema compliance; zero hallucinations. |
| **Presentation** | Streamlit Multi-Page App | 4 interactive pages: Overview, Security Analysis, Cost Analysis, AI Recommendations. Reactive provider filters. | Reactive UI filtering; clear provenance badge labeling. |
| **Verification** | Pytest + Pytest-Cov + CI Harness | Session-scoped temporary database fixtures (`tmp_path`), monkeypatched test harnesses, and mocked API clients. | Full suite passing; 67% runtime-package statement coverage; production database hash preserved. |

---

## 3. Strict Operational Boundary: Advisory Decision Support

A fundamental tenet of CLARA is its identity as an **Advisory Decision-Support Platform**:
- In production enterprise environments, autonomous write actions carry severe risks of cascading outages and data corruption.
- CLARA deliberately restricts its scope to non-destructive observability, risk prioritization, and actionable recommendation generation.
- Human cloud engineers review CLARA's recommendations, technical justifications, and projected financial savings before manually approving or executing infrastructure changes via Infrastructure-as-Code (Terraform/Ansible) workflows.
