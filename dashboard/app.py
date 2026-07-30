import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from dashboard.utils.data_access import get_overview_metrics, check_db_exists
from dashboard.components.metrics import metric_card

# Set root Streamlit configurations
st.set_page_config(page_title="CLARA", layout="wide", page_icon="☁️")

# Sidebar brand detailing CLARA pages structure
st.sidebar.title("☁️ CLARA")
st.sidebar.subheader("Cloud Risk & Cost Intelligence")

st.title("☁️ Welcome to CLARA")
st.markdown("""
**CLARA (Cloud Risk & Cost Intelligence)** is an automated cloud operations analytics platform. 
It analyzes cloud infrastructure assets, configuration parameters, daily utilization logs, and billing records to identify telemetry anomalies, calculate financial waste scores, evaluate security risks, and trigger GenAI remediation playbooks.

### Dashboard Modules:
- **Executive Overview**: Central KPIs, trend lines, and critical risk rankings.
- **Security Analysis**: Open port audits, exposure checks, and events logging.
- **Cost Optimization**: Spend by instance type, rightsizing scatter, and what-if calculators.
- **Remediation Actions**: AI remediation actions logs with approval workflow buttons.
""")

# Validate DB exists before executing queries
exists, _ = check_db_exists()
if exists:
    st.markdown("### Cloud Environment Health Overview")
    
    # Load aggregates
    metrics = get_overview_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card(
            label="Total Monitored Instances", 
            value=metrics["total_instances"]
        )
    with col2:
        metric_card(
            label="Critical Risk Nodes (Score > 70)", 
            value=metrics["critical_risk_count"]
        )
    with col3:
        metric_card(
            label="Estimated Monthly Waste", 
            value=metrics["total_monthly_waste_usd"], 
            format_as_currency=True
        )
    with col4:
        metric_card(
            label="Total Savings Opportunity", 
            value=metrics["total_potential_savings_usd"], 
            format_as_currency=True
        )
        
    st.markdown("---")
    st.info("💡 **Navigation:** Click on the page navigation links in the sidebar above to access deep-dive reports.")
