import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from dashboard.utils.data_access import (
    get_risk_by_region, 
    get_port_exposure, 
    get_vulnerability_breakdown, 
    get_security_events_timeline,
    get_all_security_configs,
    check_db_exists
)
from dashboard.components.charts import (
    risk_by_region_heatmap, 
    port_exposure_bar, 
    vulnerability_breakdown_pie, 
    security_events_timeline
)

st.set_page_config(page_title="Security Analysis - CLARA", layout="wide", page_icon="🛡️")

st.title("🛡️ Security Analysis")
st.write("Deep-dive security posture evaluation detailing open ports, encryption status, and failed authorization events.")

exists, _ = check_db_exists()
if exists:
    # 1. Charts Row 1: Region Risk & Port Exposure Side-by-side
    col1, col2 = st.columns(2)
    with col1:
        df_region = get_risk_by_region()
        fig_region = risk_by_region_heatmap(df_region)
        st.plotly_chart(fig_region, use_container_width=True)
    with col2:
        df_ports = get_port_exposure()
        fig_ports = port_exposure_bar(df_ports)
        st.plotly_chart(fig_ports, use_container_width=True)
        
    st.divider()
    
    # 2. Vulnerability distribution & Events timeline
    col3, col4 = st.columns(2)
    with col3:
        df_vuln = get_vulnerability_breakdown()
        fig_vuln = vulnerability_breakdown_pie(df_vuln)
        st.plotly_chart(fig_vuln, use_container_width=True)
    with col4:
        df_events = get_security_events_timeline()
        fig_events = security_events_timeline(df_events)
        st.plotly_chart(fig_events, use_container_width=True)
        
    st.divider()
    
    st.subheader("Configuration Vulnerability Ledger")
    
    # Summary stats (reusing df_vuln fetched above)
    exposed_count = int(df_vuln[df_vuln["vulnerability"] == "Internet Exposed"]["count"].iloc[0])
    unencrypted_count = int(df_vuln[df_vuln["vulnerability"] == "Unencrypted Volume"]["count"].iloc[0])
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.info(f"🌐 Publicly Exposed Instances: {exposed_count}")
    with col_b:
        st.warning(f"🔑 Unencrypted Storage Volumes: {unencrypted_count}")
        
    st.write("")
    
    with st.expander("Show Details for all Configurations"):
        df_configs = get_all_security_configs()
        st.dataframe(
            df_configs,
            use_container_width=True,
            column_config={
                "instance_id": st.column_config.TextColumn("Instance ID"),
                "open_ports": st.column_config.TextColumn("Open Ports"),
                "internet_exposed": st.column_config.CheckboxColumn("Internet Exposed"),
                "encryption_enabled": st.column_config.CheckboxColumn("Encryption Enabled"),
                "iam_permission_level": st.column_config.TextColumn("IAM Level"),
                "failed_logins_7d": st.column_config.NumberColumn("Failed Logins (7d)"),
                "last_patch_date": st.column_config.DateColumn("Last Patched")
            }
        )
