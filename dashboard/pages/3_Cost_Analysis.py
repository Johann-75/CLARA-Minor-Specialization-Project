import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import pandas as pd
from dashboard.utils.data_access import (
    get_cost_by_instance_type, 
    get_utilization_scatter_data, 
    get_wasteful_instances,
    get_cost_trend,
    check_db_exists
)
from dashboard.components.charts import (
    cost_by_type_donut, 
    utilization_scatter,
    utilized_vs_wasted_bar,
    cost_forecast_chart
)

st.set_page_config(page_title="Cost Analysis - CLARA", layout="wide", page_icon="💰")

st.title("💰 Financial & Cost Optimization")
st.write("Identifies idle compute resources, calculates estimated financial leakage, and ranks cost-saving opportunities.")

exists, _ = check_db_exists()
if exists:
    # 1. Charts Row
    col1, col2 = st.columns(2)
    with col1:
        df_type = get_cost_by_instance_type()
        fig_type = cost_by_type_donut(df_type)
        st.plotly_chart(fig_type, use_container_width=True)
    with col2:
        df_scatter = get_utilization_scatter_data()
        fig_scatter = utilization_scatter(df_scatter)
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    st.divider()
    
    # New Charts Row: Utilized vs Wasted Stacked Bar & 90-Day Cost Forecast
    col3, col4 = st.columns(2)
    df_waste = get_wasteful_instances(limit=50)
    with col3:
        fig_stacked = utilized_vs_wasted_bar(df_waste)
        st.plotly_chart(fig_stacked, use_container_width=True)
    with col4:
        df_trend_90 = get_cost_trend(days=90)
        fig_forecast = cost_forecast_chart(df_trend_90, forecast_days=90)
        st.plotly_chart(fig_forecast, use_container_width=True)
        
    st.divider()
    
    # 2. What-if Savings Calculator
    st.subheader("💡 What-If Savings Calculator")
    
    if df_waste.empty:
        st.info("No wasteful instances currently identified for rightsizing.")
    else:
        waste_options = df_waste["instance_id"].tolist()
        selected_instances = st.multiselect(
            "Select wasteful instances to simulate termination or rightsizing:",
            options=waste_options
        )
        
        # Calculate monthly savings for selected instances
        total_reclaimed = 0.0
        if selected_instances:
            reclaimed_df = df_waste[df_waste["instance_id"].isin(selected_instances)]
            total_reclaimed = float(reclaimed_df["estimated_savings"].sum())
            
        st.metric(
            label="Projected Monthly Savings", 
            value=f"${total_reclaimed:,.2f}", 
            delta=f"Based on {len(selected_instances)} instances simulated"
        )
        
    st.divider()
    
    # 3. Ranked Wasteful Instances list
    st.subheader("Ranked Wasteful Instances")
    st.dataframe(
        df_waste,
        use_container_width=True,
        column_config={
            "instance_id": st.column_config.TextColumn("Instance ID"),
            "instance_type": st.column_config.TextColumn("Instance Type"),
            "avg_utilization": st.column_config.NumberColumn("Avg Utilization", format="%.2f%%"),
            "monthly_cost": st.column_config.NumberColumn("Monthly Cost", format="$%.2f"),
            "estimated_savings": st.column_config.NumberColumn("Estimated Savings (90%)", format="$%.2f")
        }
    )
