"""
CLARA Operational Risk Tiers and Standard Semantics
Centralized source of truth for risk categorization, operational thresholds,
and standard color palettes across the CLARA platform.

NOTE: These tiers represent project-defined operational risk intervals on a
0.0 - 100.0 composite scale. They are NOT CVSS (Common Vulnerability Scoring
System) scores, which operate on a different 0.0 - 10.0 scale with distinct
metrics and qualitative rating boundaries.
"""

import math
from typing import Dict, Tuple, Any

# Operational Risk Tier Intervals:
# - Critical: score >= 80.0
# - High:     60.0 <= score < 80.0
# - Medium:   40.0 <= score < 60.0
# - Low:      0.0 <= score < 40.0
# - Unknown:  NULL, NaN, non-numeric, negative (< 0.0), or otherwise invalid
RISK_TIER_THRESHOLDS = {
    "Critical": 80.0,
    "High": 60.0,
    "Medium": 40.0,
    "Low": 0.0,
}

# Standardized Color Palette across CLARA
COLOR_CRITICAL = "#EF4444"  # Red
COLOR_HIGH = "#F59E0B"      # Amber / Orange
COLOR_MEDIUM = "#EAB308"    # Yellow
COLOR_LOW = "#22C55E"       # Green
COLOR_UNKNOWN = "#94A3B8"   # Neutral Slate Gray (Missing / Invalid / Negative)
COLOR_PRIMARY = "#0D9488"   # Teal / Brand Primary
COLOR_DARK = "#0F172A"      # Slate Dark
COLOR_MUTED = "#64748B"     # Slate Muted

TIER_COLORS: Dict[str, str] = {
    "Critical": COLOR_CRITICAL,
    "High": COLOR_HIGH,
    "Medium": COLOR_MEDIUM,
    "Low": COLOR_LOW,
    "Unknown": COLOR_UNKNOWN,
}

TIER_BADGES: Dict[str, str] = {
    "Critical": "🔴",
    "High": "🟠",
    "Medium": "🟡",
    "Low": "🟢",
    "Unknown": "⚪",
}

# Production Scoring Formula Weights (strictly verified against analytics/run_all_models.py)
RISK_WEIGHT_SECURITY = 0.5
RISK_WEIGHT_ANOMALY = 0.3
RISK_WEIGHT_COST_WASTE = 0.2

RISK_WEIGHTS = {
    "security": RISK_WEIGHT_SECURITY,
    "anomaly": RISK_WEIGHT_ANOMALY,
    "cost_waste": RISK_WEIGHT_COST_WASTE,
}

RISK_FORMULA_DISPLAY = "0.5 × Security + 0.3 × Anomaly + 0.2 × Cost Waste"

def classify_risk_tier(score: Any) -> str:
    """
    Classifies a composite risk score (0.0 to 100.0) into its project-defined
    operational risk tier with strict boundary semantics:
    - score >= 80.0: Critical
    - 60.0 <= score < 80.0: High
    - 40.0 <= score < 60.0: Medium
    - 0.0 <= score < 40.0: Low
    - NULL, NaN, inf, non-numeric, negative (< 0.0), or invalid: Unknown

    Invalid data is explicitly labeled 'Unknown' and is never silently clamped into Low.
    """
    if score is None:
        return "Unknown"
    try:
        val = float(score)
    except (ValueError, TypeError):
        return "Unknown"

    if math.isnan(val) or math.isinf(val) or val < 0.0:
        return "Unknown"
    elif val >= 80.0:
        return "Critical"
    elif val >= 60.0:
        return "High"
    elif val >= 40.0:
        return "Medium"
    else:
        return "Low"

def get_risk_tier_sql_case(column_name: str = "overall_risk_score") -> str:
    """
    Returns SQL CASE expression string matching the centralized risk tier definitions.
    Strictly aligns with classify_risk_tier: negative scores and NULLs map to 'Unknown'.
    """
    return f"""
        CASE 
            WHEN {column_name} IS NULL THEN 'Unknown'
            WHEN {column_name} < 0.0 THEN 'Unknown'
            WHEN {column_name} >= 80.0 THEN 'Critical'
            WHEN {column_name} >= 60.0 THEN 'High'
            WHEN {column_name} >= 40.0 THEN 'Medium'
            WHEN {column_name} >= 0.0 THEN 'Low'
            ELSE 'Unknown'
        END
    """
