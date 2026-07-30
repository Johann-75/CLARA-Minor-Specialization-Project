import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import pandas as pd
from dashboard.utils.data_access import (
    get_overview_metrics, 
    get_risk_distribution, 
    get_cost_trend, 
    get_top_critical_instances,
    check_db_exists
)
from dashboard.components.metrics import metric_card
from dashboard.components.charts import risk_distribution_pie, cost_trend_line

st.set_page_config(page_title="Executive Overview - CLARA", layout="wide", page_icon="📊")

st.title("📊 Executive Overview")
st.write("High-level overview of overall risk rankings, monthly spend histories, and critical infrastructure objects.")

exists, _ = check_db_exists()
if exists:
    # 1. Metric Cards Row
    metrics = get_overview_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Total Instances", metrics["total_instances"])
    with col2:
        metric_card("Critical Risks (Score > 70)", metrics["critical_risk_count"])
    with col3:
        metric_card("Monthly Waste", metrics["total_monthly_waste_usd"], format_as_currency=True)
    with col4:
        metric_card("Total Savings Opportunity", metrics["total_potential_savings_usd"], format_as_currency=True)
        
    st.divider()
    
    # 2. Charts Columns
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        df_risk = get_risk_distribution()
        fig_risk = risk_distribution_pie(df_risk)
        st.plotly_chart(fig_risk, use_container_width=True)
        
    with chart_col2:
        df_trend = get_cost_trend(days=30)
        fig_trend = cost_trend_line(df_trend)
        st.plotly_chart(fig_trend, use_container_width=True)
        
    st.divider()
    
    # 3. Top Critical Instances List
    st.subheader("Top Critical Instances")
    df_critical = get_top_critical_instances(limit=10)
    
    st.dataframe(
        df_critical,
        use_container_width=True,
        column_config={
            "instance_id": st.column_config.TextColumn("Instance ID"),
            "cloud_provider": st.column_config.TextColumn("Cloud"),
            "instance_type": st.column_config.TextColumn("Type"),
            "region": st.column_config.TextColumn("Region"),
            "security_risk_score": st.column_config.NumberColumn("Security Risk", format="%.1f"),
            "anomaly_score": st.column_config.NumberColumn("Anomaly Score", format="%.1f"),
            "cost_waste_score": st.column_config.NumberColumn("Cost Waste", format="%.1f"),
            "overall_risk_score": st.column_config.NumberColumn("Overall Risk Score", format="%.1f")
        }
    )
