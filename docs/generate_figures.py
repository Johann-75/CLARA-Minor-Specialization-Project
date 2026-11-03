"""
Script to generate all architectural and workflow diagrams for CLARA Final Academic Documentation.
Produces 7 high-resolution (300 DPI) figures.
Canonical Project Name: CLARA — Cloud-Linked Evaluation and Risk Assessment
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

OUT_DIR = os.path.join(os.path.dirname(__file__), "final", "figures")
os.makedirs(OUT_DIR, exist_ok=True)

# Common styling constants
PRIMARY = "#1E3A8A"      # Deep Navy Blue
SECONDARY = "#0284C7"    # Sky Blue
ACCENT = "#D97706"       # Amber / Warning
SUCCESS = "#059669"      # Emerald Green
DANGER = "#DC2626"       # Crimson Red
BG_LIGHT = "#F8FAFC"     # Light Slate Background
CARD_BG = "#FFFFFF"      # Pure White Card
TEXT_MAIN = "#0F172A"    # Deep Charcoal Text
TEXT_MUTED = "#475569"   # Muted Slate Text
BORDER_COL = "#CBD5E1"   # Border Gray


def create_architecture_overview():
    fig, ax = plt.subplots(figsize=(13, 8), dpi=300)
    ax.set_facecolor(BG_LIGHT)
    fig.patch.set_facecolor(BG_LIGHT)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 8)
    ax.axis("off")

    # Title
    ax.text(6.5, 7.6, "CLARA: Cloud-Linked Evaluation and Risk Assessment", 
            ha="center", va="center", fontsize=15, fontweight="bold", color=PRIMARY)
    ax.text(6.5, 7.25, "System Architecture: Multi-Cloud Observability, Anomaly Detection & Decision Support",
            ha="center", va="center", fontsize=9.5, style="italic", color=TEXT_MUTED)

    # 4 Vertical / Layered Tiers
    layers = [
        ("Layer 1: Data Ingestion & Multi-Cloud Generation", 5.8, 1.1, [
            ("Multi-Cloud Generators", "AWS (EC2), Azure (VM), GCP (Compute Engine)\nSynthetic 300 instances, 90-day time-series"),
            ("Data Ingestion Pipeline", "Batch CSV exports (27,000 metrics records)\n15 injected anomaly scenarios (5 classes)")
        ], PRIMARY),
        ("Layer 2: Embedded Analytical Warehouse (DuckDB)", 4.3, 1.1, [
            ("Columnar Warehouse (clara.db)", "Normalized tables: instances, daily_metrics, cost_records,\nsecurity_posture, recommendations, ml_scores"),
            ("Analytical Query Layer", "In-process vectorized OLAP aggregations, window functions,\n30-day rolling metrics, rightsizing views, zero server daemons")
        ], SECONDARY),
        ("Layer 3: Analytics & Risk Intelligence Engines", 2.8, 1.1, [
            ("Multi-Modal Anomaly Detector", "Isolation Forest (11 engineered time-series features)\n+ Contextual Security Signal scoring"),
            ("FinOps & Security Scoring", "K-Means Rightsizing (3 cost clusters, waste calc)\nDeterministic posture scorer (0-100) on observable indicators")
        ], "#7C3AED"),
        ("Layer 4: AI Decision Support & BI Presentation", 1.3, 1.1, [
            ("Dual-Engine Recommendations", "Live Google GenAI SDK (gemini-3.8-flash, Pydantic validated)\n+ Deterministic Rule Fallback (offline mode)"),
            ("Interactive Streamlit Dashboard", "4 BI Pages: Executive Overview, Security Posture,\nFinOps Rightsizing, AI Recommendation Center")
        ], SUCCESS),
    ]

    for title, y_top, height, boxes, color in layers:
        banner = patches.FancyBboxPatch((0.5, y_top), 12.0, height,
                                       boxstyle="round,pad=0.1,rounding_size=0.15",
                                       fc="#FFFFFF", ec=color, lw=1.5, zorder=2)
        ax.add_patch(banner)
        
        tag = patches.FancyBboxPatch((0.7, y_top + height - 0.28), 5.2, 0.26,
                                     boxstyle="round,pad=0.04,rounding_size=0.08",
                                     fc=color, ec=color, zorder=3)
        ax.add_patch(tag)
        ax.text(0.8, y_top + height - 0.15, title, fontsize=9, fontweight="bold", color="#FFFFFF", zorder=4)

        b1_x, b1_w = 0.8, 5.5
        b2_x, b2_w = 6.7, 5.5
        box_y = y_top + 0.12
        box_h = height - 0.45

        for bx, bw, (btitle, bdesc) in [(b1_x, b1_w, boxes[0]), (b2_x, b2_w, boxes[1])]:
            sub_patch = patches.FancyBboxPatch((bx, box_y), bw, box_h,
                                              boxstyle="round,pad=0.06,rounding_size=0.08",
                                              fc="#F8FAFC", ec=BORDER_COL, lw=1.0, zorder=3)
            ax.add_patch(sub_patch)
            ax.text(bx + 0.2, box_y + box_h - 0.2, btitle, fontsize=9, fontweight="bold", color=TEXT_MAIN, zorder=4)
            ax.text(bx + 0.2, box_y + box_h - 0.45, bdesc, fontsize=7.5, color=TEXT_MUTED, va="top", zorder=4)

    for y_arrow in [5.8, 4.3, 2.8]:
        ax.annotate("", xy=(6.5, y_arrow), xytext=(6.5, y_arrow + 0.2),
                    arrowprops=dict(arrowstyle="->", color=PRIMARY, lw=2.0), zorder=5)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "architecture_overview.png"), dpi=300)
    plt.close()
    print("Created architecture_overview.png")


def create_data_pipeline_flow():
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)
    ax.set_facecolor(BG_LIGHT)
    fig.patch.set_facecolor(BG_LIGHT)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.5)
    ax.axis("off")

    ax.text(6.0, 6.1, "CLARA: Multi-Cloud Telemetry & Ingestion Pipeline", 
            ha="center", va="center", fontsize=15, fontweight="bold", color=PRIMARY)
    ax.text(6.0, 5.75, "Synthetic Multi-Cloud Data Generation, Anomaly Injection, and DuckDB Ingestion",
            ha="center", va="center", fontsize=9.5, style="italic", color=TEXT_MUTED)

    steps = [
        (0.6, 2.0, 2.3, 3.2, "1. Synthetic Generator", 
         "generate_synthetic_data.py\n\n• 300 Multi-Cloud Instances\n  - AWS (100 EC2)\n  - Azure (100 VM)\n  - GCP (100 Compute)\n• 90-Day Telemetry Window\n• 27,000 Daily Metric Rows\n• 27,000 Cost Records", SECONDARY),
        (3.4, 2.0, 2.3, 3.2, "2. Ground-Truth Anomaly", 
         "anomaly_manifest.json\n\n• 15 Injected Scenarios\n• 5 Anomaly Categories:\n  - cpu_spike (3)\n  - memory_leak (3)\n  - network_exfiltration (3)\n  - brute_force (3)\n  - misconfiguration (3)\n• Manifest held out from ML", ACCENT),
        (6.2, 2.0, 2.3, 3.2, "3. Raw Ingestion Layer", 
         "data/synthetic/*.csv\n\n• instances.csv\n• daily_metrics.csv\n• cost_records.csv\n• security_posture.csv\n• Strict Schema Validation\n• Atomic CSV Generation\n• Seed=42 Reproducibility", "#6366F1"),
        (9.0, 2.0, 2.4, 3.2, "4. Embedded DuckDB", 
         "warehouse/clara.db\n\n• In-Process Columnar Storage\n• ACID Relational Operations\n• 6 Production Tables\n• Analytical Views & Indices\n• Deterministic Backups\n• Zero Network Daemon", SUCCESS),
    ]

    for x, y, w, h, header, body, col in steps:
        card = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1,rounding_size=0.12",
                                      fc=CARD_BG, ec=col, lw=1.8, zorder=2)
        ax.add_patch(card)
        hdr_bar = patches.FancyBboxPatch((x, y + h - 0.45), w, 0.45,
                                         boxstyle="round,pad=0.02,rounding_size=0.08",
                                         fc=col, ec=col, zorder=3)
        ax.add_patch(hdr_bar)
        ax.text(x + w/2, y + h - 0.22, header, ha="center", va="center", 
                fontsize=9, fontweight="bold", color="#FFFFFF", zorder=4)
        ax.text(x + 0.15, y + h - 0.65, body, ha="left", va="top", 
                fontsize=8, color=TEXT_MAIN, zorder=4, linespacing=1.35)

    for arrow_x in [2.95, 5.75, 8.55]:
        ax.annotate("", xy=(arrow_x + 0.4, 3.6), xytext=(arrow_x, 3.6),
                    arrowprops=dict(arrowstyle="->", color=PRIMARY, lw=2.5), zorder=5)

    btm = patches.FancyBboxPatch((0.6, 0.5), 10.8, 1.1, boxstyle="round,pad=0.08,rounding_size=0.1",
                                fc="#EFF6FF", ec="#BFDBFE", lw=1.0, zorder=2)
    ax.add_patch(btm)
    ax.text(0.9, 1.25, "Key Implementation Features:", fontsize=8.5, fontweight="bold", color=PRIMARY, zorder=3)
    ax.text(0.9, 0.72, "• Evaluation Isolation: anomaly_manifest.json is strictly isolated and never touched by ML feature extraction or inference.\n• High Analytical Performance: DuckDB vectorized bulk loader ingests telemetry in-process with zero external server daemons.\n• Test Isolation: All test runs create temporary databases in tmp_path, completely preserving production clara.db.",
            fontsize=7.5, color=TEXT_MUTED, va="top", zorder=3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "data_pipeline_flow.png"), dpi=300)
    plt.close()
    print("Created data_pipeline_flow.png")


def create_risk_scoring_flow():
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)
    ax.set_facecolor(BG_LIGHT)
    fig.patch.set_facecolor(BG_LIGHT)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.5)
    ax.axis("off")

    ax.text(6.0, 6.1, "CLARA: Composite Risk Scoring Formulation & Operational Tiers", 
            ha="center", va="center", fontsize=15, fontweight="bold", color=PRIMARY)
    ax.text(6.0, 5.75, "Tri-Factor Mathematical Risk Weighting and Unified Centralized Severity Classification",
            ha="center", va="center", fontsize=9.5, style="italic", color=TEXT_MUTED)

    pillars = [
        (0.6, 3.2, 2.8, 2.1, "Security Posture Score (0-100)", 
         "Weight: 50% (0.5)\n\n• Deterministic Rule Scoring\n• Observable Vulnerabilities\n• IAM Permission Level\n• Ingress Port Exposure\n• Security-Event Indicators", DANGER),
        (4.0, 3.2, 2.8, 2.1, "Telemetry Anomaly Score (0-100)", 
         "Weight: 30% (0.3)\n\n• Isolation Forest Telemetry Score\n• Short & Long Rolling Trends\n• Contextual Security Signal\n• Calibrated Anomaly Flag", ACCENT),
        (7.4, 3.2, 2.8, 2.1, "Cost Waste Score (0-100)", 
         "Weight: 20% (0.2)\n\n• K-Means FinOps Rightsizing\n• Low CPU & RAM Utilization\n• Actionable Cost Waste Calculation\n• Cost-Waste Normalized Ratio", SECONDARY),
    ]

    for x, y, w, h, header, body, col in pillars:
        card = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.1",
                                      fc=CARD_BG, ec=col, lw=1.5, zorder=2)
        ax.add_patch(card)
        hdr = patches.FancyBboxPatch((x, y + h - 0.4), w, 0.4, boxstyle="round,pad=0.02,rounding_size=0.06",
                                     fc=col, ec=col, zorder=3)
        ax.add_patch(hdr)
        ax.text(x + w/2, y + h - 0.2, header, ha="center", va="center",
                fontsize=8.5, fontweight="bold", color="#FFFFFF", zorder=4)
        ax.text(x + 0.15, y + h - 0.55, body, ha="left", va="top",
                fontsize=8, color=TEXT_MAIN, zorder=4, linespacing=1.3)

    formula_box = patches.FancyBboxPatch((1.5, 1.8), 7.8, 0.95, boxstyle="round,pad=0.08,rounding_size=0.12",
                                        fc="#EDE9FE", ec="#8B5CF6", lw=1.8, zorder=2)
    ax.add_patch(formula_box)
    ax.text(5.4, 2.45, "Composite Risk Score = (0.50 × Security) + (0.30 × Anomaly) + (0.20 × Cost Waste)",
            ha="center", va="center", fontsize=10, fontweight="bold", color="#5B21B6", zorder=4)
    ax.text(5.4, 2.05, "Calibrated bounded score in range [0.0, 100.0] with mathematical consistency across CLI & Dashboard",
            ha="center", va="center", fontsize=8, color=TEXT_MUTED, zorder=4)

    for px in [2.0, 5.4, 8.8]:
        ax.annotate("", xy=(px if px==5.4 else (4.0 if px<5 else 6.8), 2.8), xytext=(px, 3.2),
                    arrowprops=dict(arrowstyle="->", color=PRIMARY, lw=2.0), zorder=5)

    ax.annotate("", xy=(5.4, 1.3), xytext=(5.4, 1.8),
                arrowprops=dict(arrowstyle="->", color=PRIMARY, lw=2.5), zorder=5)

    tiers = [
        (0.6, 0.4, 2.0, 0.8, "CRITICAL\nScore ≥ 80.0", "#FEE2E2", DANGER),
        (2.8, 0.4, 2.0, 0.8, "HIGH\n60.0 ≤ Score < 80.0", "#FFEDD5", ACCENT),
        (5.0, 0.4, 2.0, 0.8, "MEDIUM\n40.0 ≤ Score < 60.0", "#FEF08A", "#CA8A04"),
        (7.2, 0.4, 2.0, 0.8, "LOW\n0.0 ≤ Score < 40.0", "#DCFCE7", SUCCESS),
        (9.4, 0.4, 2.0, 0.8, "UNKNOWN\nMissing / Invalid", "#F1F5F9", "#64748B"),
    ]

    for tx, ty, tw, th, ttext, tbg, tcol in tiers:
        tbox = patches.FancyBboxPatch((tx, ty), tw, th, boxstyle="round,pad=0.06,rounding_size=0.08",
                                     fc=tbg, ec=tcol, lw=1.5, zorder=2)
        ax.add_patch(tbox)
        ax.text(tx + tw/2, ty + th/2, ttext, ha="center", va="center",
                fontsize=7.5, fontweight="bold", color=tcol, zorder=4)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "risk_scoring_flow.png"), dpi=300)
    plt.close()
    print("Created risk_scoring_flow.png")


def create_anomaly_detector_pipeline():
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)
    ax.set_facecolor(BG_LIGHT)
    fig.patch.set_facecolor(BG_LIGHT)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.5)
    ax.axis("off")

    ax.text(6.0, 6.1, "CLARA: Multi-Modal Anomaly Detection Engine", 
            ha="center", va="center", fontsize=15, fontweight="bold", color=PRIMARY)
    ax.text(6.0, 5.75, "Engineered Time-Series Features, Isolation Forest Model, and Contextual Security Integration",
            ha="center", va="center", fontsize=9.5, style="italic", color=TEXT_MUTED)

    s1 = patches.FancyBboxPatch((0.6, 1.8), 3.4, 3.6, boxstyle="round,pad=0.1,rounding_size=0.12",
                               fc=CARD_BG, ec=SECONDARY, lw=1.8, zorder=2)
    ax.add_patch(s1)
    s1_hdr = patches.FancyBboxPatch((0.6, 5.0), 3.4, 0.4, boxstyle="round,pad=0.02,rounding_size=0.06",
                                   fc=SECONDARY, ec=SECONDARY, zorder=3)
    ax.add_patch(s1_hdr)
    ax.text(2.3, 5.2, "11 Engineered Time-Series Features", ha="center", va="center",
            fontsize=8.5, fontweight="bold", color="#FFFFFF", zorder=4)
    features_text = (
        "• max_robust_z_cpu (outlier spike)\n"
        "• max_robust_z_mem (memory outlier)\n"
        "• max_robust_z_net (exfiltration)\n"
        "• max_robust_z_disk (I/O burst)\n"
        "• max_day_to_day_cpu (short-term change)\n"
        "• peak_to_median_net (burstiness)\n"
        "• dev_7d_vs_30d_cpu (medium divergence)\n"
        "• dev_7d_vs_30d_net (data volume shift)\n"
        "• max_rolling_slope_mem (gradual leak)\n"
        "• combined_spike_signal (multi-resource)\n"
        "• net_disk_interaction (correlated load)"
    )
    ax.text(0.8, 4.85, features_text, ha="left", va="top", fontsize=7.5, color=TEXT_MAIN, zorder=4, linespacing=1.25)

    s2 = patches.FancyBboxPatch((4.3, 1.8), 3.4, 3.6, boxstyle="round,pad=0.1,rounding_size=0.12",
                               fc=CARD_BG, ec="#7C3AED", lw=1.8, zorder=2)
    ax.add_patch(s2)
    s2_hdr = patches.FancyBboxPatch((4.3, 5.0), 3.4, 0.4, boxstyle="round,pad=0.02,rounding_size=0.06",
                                   fc="#7C3AED", ec="#7C3AED", zorder=3)
    ax.add_patch(s2_hdr)
    ax.text(6.0, 5.2, "Isolation Forest Scoring", ha="center", va="center",
            fontsize=8.5, fontweight="bold", color="#FFFFFF", zorder=4)
    model_text = (
        "• Model: Isolation Forest\n"
        "  - n_estimators = 150 trees\n"
        "  - contamination = 0.05\n"
        "  - random_state = 42 (reproducible)\n\n"
        "• Telemetry Anomaly Score:\n"
        "  - Calibrated raw decision function\n"
        "  - Min-max mapped to [0.0, 100.0]\n\n"
        "• Security Contextual Score:\n"
        "  - Observable vulnerability indicators\n"
        "  - Ingress open ports (22, 3389)\n"
        "  - High IAM privilege level"
    )
    ax.text(4.5, 4.85, model_text, ha="left", va="top", fontsize=7.5, color=TEXT_MAIN, zorder=4, linespacing=1.25)

    s3 = patches.FancyBboxPatch((8.0, 1.8), 3.4, 3.6, boxstyle="round,pad=0.1,rounding_size=0.12",
                               fc=CARD_BG, ec=SUCCESS, lw=1.8, zorder=2)
    ax.add_patch(s3)
    s3_hdr = patches.FancyBboxPatch((8.0, 5.0), 3.4, 0.4, boxstyle="round,pad=0.02,rounding_size=0.06",
                                   fc=SUCCESS, ec=SUCCESS, zorder=3)
    ax.add_patch(s3_hdr)
    ax.text(9.7, 5.2, "Operational Decision Output", ha="center", va="center",
            fontsize=8.5, fontweight="bold", color="#FFFFFF", zorder=4)
    eval_text = (
        "• Operational Triage Threshold = 65.0\n\n"
        "• Evaluation Results (Seed-42):\n"
        "  - Precision: 82.35% (≥ 80% req.)\n"
        "  - Recall: 93.33% (≥ 85% req.)\n"
        "  - F1-Score: 0.8750\n"
        "  - True Positives: 14 / 15\n"
        "  - False Positives: 3\n\n"
        "• Honest Per-Category Recall:\n"
        "  cpu_spike: 3/3 (100%)\n"
        "  brute_force: 3/3 (100%)\n"
        "  network_exfiltration: 3/3 (100%)\n"
        "  misconfiguration: 3/3 (100%)\n"
        "  memory_leak: 2/3 (66.7%)"
    )
    ax.text(8.2, 4.85, eval_text, ha="left", va="top", fontsize=7.5, color=TEXT_MAIN, zorder=4, linespacing=1.25)

    ax.annotate("", xy=(4.3, 3.6), xytext=(4.0, 3.6),
                arrowprops=dict(arrowstyle="->", color=PRIMARY, lw=2.5), zorder=5)
    ax.annotate("", xy=(8.0, 3.6), xytext=(7.7, 3.6),
                arrowprops=dict(arrowstyle="->", color=PRIMARY, lw=2.5), zorder=5)

    note = patches.FancyBboxPatch((0.6, 0.5), 10.8, 0.9, boxstyle="round,pad=0.08,rounding_size=0.1",
                                 fc="#F0FDF4", ec="#BBF7D0", lw=1.0, zorder=2)
    ax.add_patch(note)
    ax.text(0.8, 1.15, "Evaluation Integrity Note:", fontsize=8, fontweight="bold", color=SUCCESS, zorder=3)
    ax.text(0.8, 0.70, "• Category Breadth: All 5 anomaly categories had at least one detected instance (14/15 TP overall).\n• Operational Context: Threshold 65/100 is a project-defined operational triage threshold, distinct from CVSS intervals.",
            fontsize=7.2, color=TEXT_MUTED, va="top", zorder=3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "anomaly_detector_pipeline.png"), dpi=300)
    plt.close()
    print("Created anomaly_detector_pipeline.png")


def create_gemini_recommendation_flow():
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)
    ax.set_facecolor(BG_LIGHT)
    fig.patch.set_facecolor(BG_LIGHT)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.5)
    ax.axis("off")

    ax.text(6.0, 6.1, "CLARA: Dual-Engine Recommendation Architecture", 
            ha="center", va="center", fontsize=15, fontweight="bold", color=PRIMARY)
    ax.text(6.0, 5.75, "Modern Google GenAI SDK (gemini-3.8-flash) & Deterministic Offline Rule Fallback",
            ha="center", va="center", fontsize=9.5, style="italic", color=TEXT_MUTED)

    top = patches.FancyBboxPatch((3.5, 4.4), 5.0, 0.95, boxstyle="round,pad=0.08,rounding_size=0.1",
                                fc=CARD_BG, ec=PRIMARY, lw=1.5, zorder=2)
    ax.add_patch(top)
    ax.text(6.0, 5.05, "Recommendation Orchestrator (run_recommendations.py)", 
            ha="center", va="center", fontsize=9, fontweight="bold", color=PRIMARY, zorder=4)
    ax.text(6.0, 4.65, "Triage candidate instances from risk & anomaly scores\nLoad GEMINI_API_KEY securely from environment",
            ha="center", va="center", fontsize=7.5, color=TEXT_MUTED, zorder=4)

    dec = patches.Polygon([[6.0, 4.0], [7.2, 3.4], [6.0, 2.8], [4.8, 3.4]],
                          fc="#EFF6FF", ec=PRIMARY, lw=1.5, zorder=3)
    ax.add_patch(dec)
    ax.text(6.0, 3.4, "Valid Key\nPresent?", ha="center", va="center", 
            fontsize=7.5, fontweight="bold", color=PRIMARY, zorder=4)

    ax.annotate("", xy=(6.0, 4.0), xytext=(6.0, 4.4),
                arrowprops=dict(arrowstyle="<-", color=PRIMARY, lw=1.5), zorder=5)

    p1 = patches.FancyBboxPatch((0.5, 1.4), 4.2, 2.0, boxstyle="round,pad=0.08,rounding_size=0.1",
                               fc=CARD_BG, ec=SUCCESS, lw=1.5, zorder=2)
    ax.add_patch(p1)
    p1_hdr = patches.FancyBboxPatch((0.5, 3.0), 4.2, 0.4, boxstyle="round,pad=0.02,rounding_size=0.06",
                                   fc=SUCCESS, ec=SUCCESS, zorder=3)
    ax.add_patch(p1_hdr)
    ax.text(2.6, 3.2, "LIVE GEMINI ENGINE", ha="center", va="center",
            fontsize=8.5, fontweight="bold", color="#FFFFFF", zorder=4)
    p1_text = (
        "• Modern google-genai SDK (gemini-3.8-flash)\n"
        "• Pydantic Schema Validation (RecommendationList)\n"
        "• Anti-Hallucination Guard: instance ID verification\n"
        "• Application-Controlled Provenance:\n"
        "  - generation_source = 'gemini'\n"
        "  - model_name = 'gemini-3.8-flash'\n"
        "  - fallback_reason = NULL"
    )
    ax.text(0.7, 2.85, p1_text, ha="left", va="top", fontsize=7.2, color=TEXT_MAIN, zorder=4, linespacing=1.2)

    p2 = patches.FancyBboxPatch((7.3, 1.4), 4.2, 2.0, boxstyle="round,pad=0.08,rounding_size=0.1",
                               fc=CARD_BG, ec=ACCENT, lw=1.5, zorder=2)
    ax.add_patch(p2)
    p2_hdr = patches.FancyBboxPatch((7.3, 3.0), 4.2, 0.4, boxstyle="round,pad=0.02,rounding_size=0.06",
                                   fc=ACCENT, ec=ACCENT, zorder=3)
    ax.add_patch(p2_hdr)
    ax.text(9.4, 3.2, "OFFLINE RULE ENGINE", ha="center", va="center",
            fontsize=8.5, fontweight="bold", color="#FFFFFF", zorder=4)
    p2_text = (
        "• Deterministic Domain Heuristics\n"
        "• Zero Network / API Key Requirement\n"
        "• Safe Fallback for Quota / Network Drops\n"
        "• Explicit Honest Provenance Labeling:\n"
        "  - generation_source = 'offline_fallback'\n"
        "  - model_name = 'deterministic_rule_engine'\n"
        "  - fallback_reason = 'missing_key' | 'api_error'"
    )
    ax.text(7.5, 2.85, p2_text, ha="left", va="top", fontsize=7.2, color=TEXT_MAIN, zorder=4, linespacing=1.2)

    ax.annotate("Yes", xy=(2.6, 3.4), xytext=(4.8, 3.4),
                arrowprops=dict(arrowstyle="->", color=SUCCESS, lw=1.8), zorder=5)
    ax.annotate("", xy=(2.6, 3.4), xytext=(2.6, 3.0),
                arrowprops=dict(arrowstyle="-", color=SUCCESS, lw=1.8), zorder=5)

    ax.annotate("No", xy=(9.4, 3.4), xytext=(7.2, 3.4),
                arrowprops=dict(arrowstyle="->", color=ACCENT, lw=1.8), zorder=5)
    ax.annotate("", xy=(9.4, 3.4), xytext=(9.4, 3.0),
                arrowprops=dict(arrowstyle="-", color=ACCENT, lw=1.8), zorder=5)

    btm = patches.FancyBboxPatch((3.0, 0.3), 6.0, 0.75, boxstyle="round,pad=0.08,rounding_size=0.1",
                                fc="#F8FAFC", ec=PRIMARY, lw=1.5, zorder=2)
    ax.add_patch(btm)
    ax.text(6.0, 0.75, "Analytical Warehouse (clara.db -> recommendations table)", 
            ha="center", va="center", fontsize=8.5, fontweight="bold", color=PRIMARY, zorder=4)
    ax.text(6.0, 0.5, "10 Verified Live Gemini Records | Provenance Stored & Displayed in Dashboard",
            ha="center", va="center", fontsize=7.2, color=TEXT_MUTED, zorder=4)

    ax.annotate("", xy=(4.5, 1.05), xytext=(2.6, 1.4),
                arrowprops=dict(arrowstyle="->", color=SUCCESS, lw=1.5), zorder=5)
    ax.annotate("", xy=(7.5, 1.05), xytext=(9.4, 1.4),
                arrowprops=dict(arrowstyle="->", color=ACCENT, lw=1.5), zorder=5)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "gemini_recommendation_flow.png"), dpi=300)
    plt.close()
    print("Created gemini_recommendation_flow.png")


def create_duckdb_schema_erd():
    fig, ax = plt.subplots(figsize=(13, 7.5), dpi=300)
    ax.set_facecolor(BG_LIGHT)
    fig.patch.set_facecolor(BG_LIGHT)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 7.5)
    ax.axis("off")

    ax.text(6.5, 7.1, "CLARA: DuckDB Relational Warehouse Schema (ERD)", 
            ha="center", va="center", fontsize=15, fontweight="bold", color=PRIMARY)
    ax.text(6.5, 6.75, "Entity-Relationship Architecture across Telemetry, Cost, Security, and Recommendations",
            ha="center", va="center", fontsize=9.5, style="italic", color=TEXT_MUTED)

    tables = [
        (0.6, 3.4, 3.4, 3.0, "cloud_instances (Core)", [
            ("instance_id", "VARCHAR [PK]"),
            ("cloud_provider", "VARCHAR (AWS/Azure/GCP)"),
            ("region", "VARCHAR"),
            ("instance_type", "VARCHAR"),
            ("cpu_cores", "INTEGER"),
            ("memory_gb", "INTEGER"),
            ("launch_date", "DATE"),
            ("status", "VARCHAR"),
            ("hourly_rate_usd", "DOUBLE")
        ], PRIMARY),

        (4.8, 3.7, 3.4, 2.7, "metrics_daily (Telemetry)", [
            ("instance_id", "VARCHAR [FK]"),
            ("date", "DATE"),
            ("cpu_utilization_pct", "DOUBLE"),
            ("memory_utilization_pct", "DOUBLE"),
            ("network_in_mb", "DOUBLE"),
            ("network_out_mb", "DOUBLE"),
            ("disk_read_iops", "INTEGER"),
            ("disk_write_iops", "INTEGER")
        ], SECONDARY),

        (9.0, 3.7, 3.4, 2.7, "cost_data (FinOps)", [
            ("instance_id", "VARCHAR [FK]"),
            ("date", "DATE"),
            ("hourly_cost_usd", "DOUBLE"),
            ("daily_cost_usd", "DOUBLE"),
            ("utilization_pct", "DOUBLE"),
            ("waste_score", "DOUBLE")
        ], "#059669"),

        (0.6, 0.4, 3.4, 2.6, "security_configurations", [
            ("instance_id", "VARCHAR [FK]"),
            ("open_ports", "VARCHAR"),
            ("internet_exposed", "BOOLEAN"),
            ("encryption_enabled", "BOOLEAN"),
            ("iam_permission_level", "VARCHAR"),
            ("failed_logins_7d", "INTEGER"),
            ("last_patch_date", "DATE")
        ], DANGER),

        (4.8, 0.4, 3.4, 2.8, "risk_scores (ML Scores)", [
            ("score_id", "VARCHAR [PK]"),
            ("instance_id", "VARCHAR [FK]"),
            ("anomaly_score", "DOUBLE"),
            ("security_risk_score", "DOUBLE"),
            ("cost_waste_score", "DOUBLE"),
            ("overall_risk_score", "DOUBLE"),
            ("model_version", "VARCHAR"),
            ("calculated_at", "TIMESTAMP")
        ], "#7C3AED"),

        (9.0, 0.4, 3.4, 2.8, "recommendations (AI / Rules)", [
            ("recommendation_id", "VARCHAR [PK]"),
            ("instance_id", "VARCHAR [FK]"),
            ("title", "VARCHAR"),
            ("description", "VARCHAR"),
            ("estimated_savings_usd", "DOUBLE"),
            ("generation_source", "VARCHAR (gemini/offline)"),
            ("model_name", "VARCHAR"),
            ("fallback_reason", "VARCHAR [NULLable]")
        ], ACCENT),
    ]

    for x, y, w, h, tname, fields, col in tables:
        card = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.1",
                                      fc=CARD_BG, ec=col, lw=1.5, zorder=2)
        ax.add_patch(card)
        hdr = patches.FancyBboxPatch((x, y + h - 0.38), w, 0.38, boxstyle="round,pad=0.02,rounding_size=0.06",
                                     fc=col, ec=col, zorder=3)
        ax.add_patch(hdr)
        ax.text(x + w/2, y + h - 0.19, tname, ha="center", va="center",
                fontsize=8.5, fontweight="bold", color="#FFFFFF", zorder=4)
        
        for fidx, (fname, ftype) in enumerate(fields):
            fy = y + h - 0.58 - (fidx * 0.24)
            pk_star = "*" if "[PK]" in ftype else ("#" if "[FK]" in ftype else " ")
            ax.text(x + 0.15, fy, f"{pk_star} {fname}", fontsize=7.2, fontweight="bold" if pk_star != " " else "normal", color=TEXT_MAIN, zorder=4)
            ax.text(x + w - 0.15, fy, ftype.split()[0], ha="right", fontsize=6.8, color=TEXT_MUTED, zorder=4)

    ax.annotate("", xy=(4.8, 5.0), xytext=(4.0, 5.0),
                arrowprops=dict(arrowstyle="->", color=PRIMARY, lw=1.5), zorder=5)
    ax.annotate("", xy=(9.0, 5.0), xytext=(8.2, 5.0),
                arrowprops=dict(arrowstyle="->", color=PRIMARY, lw=1.5), zorder=5)
    ax.annotate("", xy=(2.3, 3.0), xytext=(2.3, 3.4),
                arrowprops=dict(arrowstyle="->", color=PRIMARY, lw=1.5), zorder=5)
    ax.annotate("", xy=(4.8, 1.8), xytext=(4.0, 4.0),
                arrowprops=dict(arrowstyle="->", color=PRIMARY, lw=1.5), zorder=5)
    ax.annotate("", xy=(9.0, 1.8), xytext=(4.0, 3.8),
                arrowprops=dict(arrowstyle="->", color=PRIMARY, lw=1.5), zorder=5)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "duckdb_schema_erd.png"), dpi=300)
    plt.close()
    print("Created duckdb_schema_erd.png")


def create_testing_validation_flow():
    fig, ax = plt.subplots(figsize=(12, 6.0), dpi=300)
    ax.set_facecolor(BG_LIGHT)
    fig.patch.set_facecolor(BG_LIGHT)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.0)
    ax.axis("off")

    ax.text(6.0, 5.6, "CLARA: Test Isolation & CI/CD Verification Architecture", 
            ha="center", va="center", fontsize=15, fontweight="bold", color=PRIMARY)
    ax.text(6.0, 5.25, "Session-Scoped Temporary DuckDB Harness, Mocked External APIs, and 67% Runtime-Package Coverage",
            ha="center", va="center", fontsize=9.5, style="italic", color=TEXT_MUTED)

    blocks = [
        (0.6, 1.5, 3.4, 3.4, "1. Test Isolation Harness", 
         "tests/conftest.py\n\n• Session-scoped tmp_path fixture\n• Temporary DuckDB database created\n• Zero writes to root clara.db\n• Root CSVs completely untouched\n• Deterministic fixtures seeded in temp DB\n• Mocked Google GenAI client\n• Network calls blocked in tests", SECONDARY),
        (4.3, 1.5, 3.4, 3.4, "2. Test Suite Execution", 
         "pytest -v (82/82 Passing)\n\n• test_synthetic_data: generation & schema\n• test_duckdb: ACID & analytical views\n• test_anomaly_detector: 11 features & IF\n• test_cost_clusters: K-Means rightsizing\n• test_security_score: posture bounds\n• test_gemini_client: mock schema & errors\n• test_dashboard: filters, risk tiers, parity", "#7C3AED"),
        (8.0, 1.5, 3.4, 3.4, "3. Quality Verification Gates", 
         "pytest --cov --cov-report=term-missing\n\n• Runtime-Package Coverage: 67%\n• Production DuckDB Bit-for-Bit Safe\n• Zero Exposed API Keys or Secrets\n• Anomaly Detection Gate:\n  - Precision: 82.35% (≥ 80% req)\n  - Recall: 93.33% (≥ 85% req)\n  - F1-Score: 0.8750\n• GitHub Actions CI Compatibility", SUCCESS),
    ]

    for x, y, w, h, header, body, col in blocks:
        card = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1,rounding_size=0.12",
                                      fc=CARD_BG, ec=col, lw=1.8, zorder=2)
        ax.add_patch(card)
        hdr = patches.FancyBboxPatch((x, y + h - 0.45), w, 0.45, boxstyle="round,pad=0.02,rounding_size=0.08",
                                     fc=col, ec=col, zorder=3)
        ax.add_patch(hdr)
        ax.text(x + w/2, y + h - 0.22, header, ha="center", va="center",
                fontsize=9, fontweight="bold", color="#FFFFFF", zorder=4)
        ax.text(x + 0.15, y + h - 0.65, body, ha="left", va="top", 
                fontsize=8, color=TEXT_MAIN, zorder=4, linespacing=1.3)

    ax.annotate("", xy=(4.3, 3.2), xytext=(4.0, 3.2),
                arrowprops=dict(arrowstyle="->", color=PRIMARY, lw=2.5), zorder=5)
    ax.annotate("", xy=(8.0, 3.2), xytext=(7.7, 3.2),
                arrowprops=dict(arrowstyle="->", color=PRIMARY, lw=2.5), zorder=5)

    pill = patches.FancyBboxPatch((0.6, 0.4), 10.8, 0.75, boxstyle="round,pad=0.08,rounding_size=0.1",
                                 fc="#EFF6FF", ec="#BFDBFE", lw=1.2, zorder=2)
    ax.add_patch(pill)
    ax.text(6.0, 0.78, "Verification Summary: 82/82 Tests Passed | 67% Runtime-Package Coverage | Production Database Preserved",
            ha="center", va="center", fontsize=8.5, fontweight="bold", color=PRIMARY, zorder=4)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "testing_validation_flow.png"), dpi=300)
    plt.close()
    print("Created testing_validation_flow.png")


if __name__ == "__main__":
    create_architecture_overview()
    create_data_pipeline_flow()
    create_risk_scoring_flow()
    create_anomaly_detector_pipeline()
    create_gemini_recommendation_flow()
    create_duckdb_schema_erd()
    create_testing_validation_flow()
    print("All 7 architectural diagrams regenerated with canonical title and corrected language!")
