import os
from collections import Counter
from typing import Optional, List, Dict
import streamlit as st
import pandas as pd
import duckdb

from dashboard.utils.risk_tiers import (
    classify_risk_tier,
    get_risk_tier_sql_case,
    RISK_TIER_THRESHOLDS
)

DB_PATH = "clara.db"

def check_db_exists() -> tuple[bool, Optional[str]]:
    """
    Checks if the clara.db file exists in the project root.
    If it is missing, renders st.error and returns False.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    full_path = os.path.join(project_root, DB_PATH)
    if not os.path.exists(full_path):
        try:
            st.error("Database not found. Run the data generator, warehouse loader, and analytics models first (see README).")
        except Exception:
            print("Database not found at:", full_path)
        return False, None
    return True, full_path

def get_read_only_conn():
    """
    Helper to establish a read-only DuckDB connection.
    """
    exists, path = check_db_exists()
    if not exists:
        raise FileNotFoundError("clara.db file is missing.")
    return duckdb.connect(path, read_only=True)

@st.cache_data(ttl=300)
def get_cloud_providers() -> List[str]:
    """
    Retrieves distinct cloud provider names for filtering controls.
    """
    conn = None
    try:
        conn = get_read_only_conn()
        providers = [r[0] for r in conn.execute("SELECT DISTINCT cloud_provider FROM cloud_instances WHERE cloud_provider IS NOT NULL ORDER BY cloud_provider").fetchall()]
        return ["All"] + providers
    except Exception as e:
        print(f"Dashboard [Providers]: Error {e}")
        return ["All"]
    finally:
        if conn:
            conn.close()

@st.cache_data(ttl=300)
def get_regions(provider: Optional[str] = None) -> List[str]:
    """
    Retrieves distinct regions with optional provider filter for dropdown controls.
    """
    conn = None
    try:
        conn = get_read_only_conn()
        if provider and provider != "All":
            regions = [r[0] for r in conn.execute("SELECT DISTINCT region FROM cloud_instances WHERE cloud_provider = ? ORDER BY region", (provider,)).fetchall()]
        else:
            regions = [r[0] for r in conn.execute("SELECT DISTINCT region FROM cloud_instances WHERE region IS NOT NULL ORDER BY region").fetchall()]
        return ["All"] + regions
    except Exception as e:
        print(f"Dashboard [Regions]: Error {e}")
        return ["All"]
    finally:
        if conn:
            conn.close()

@st.cache_data(ttl=300)
def get_overview_metrics(provider: Optional[str] = None, region: Optional[str] = None) -> dict:
    """
    Queries overall metrics aggregates across the fleet with optional provider and region filters.
    Threshold for Critical risk instances is strictly aligned with centralized operational risk semantics (>= 80.0).
    """
    conn = None
    try:
        conn = get_read_only_conn()
        
        provider_clause = " AND ci.cloud_provider = ?" if provider and provider != "All" else ""
        region_clause = " AND ci.region = ?" if region and region != "All" else ""
        
        args = []
        if provider and provider != "All":
            args.append(provider)
        if region and region != "All":
            args.append(region)
        args_tuple = tuple(args)

        # 1. Total instances
        q_inst = f"SELECT COUNT(*) FROM cloud_instances ci WHERE 1=1 {provider_clause} {region_clause}"
        total_inst = conn.execute(q_inst, args_tuple).fetchone()[0]

        # 2. Critical Risk Instances (score >= 80.0)
        q_crit = f"""
            SELECT COUNT(*) 
            FROM risk_scores rs
            JOIN cloud_instances ci ON rs.instance_id = ci.instance_id
            WHERE rs.overall_risk_score >= 80.0 {provider_clause} {region_clause}
        """
        critical_risk = conn.execute(q_crit, args_tuple).fetchone()[0]

        # 3. High Risk Instances (60.0 <= score < 80.0)
        q_high = f"""
            SELECT COUNT(*) 
            FROM risk_scores rs
            JOIN cloud_instances ci ON rs.instance_id = ci.instance_id
            WHERE rs.overall_risk_score >= 60.0 AND rs.overall_risk_score < 80.0 {provider_clause} {region_clause}
        """
        high_risk = conn.execute(q_high, args_tuple).fetchone()[0]

        # 4. Actionable Monthly Waste (sum of recommendations where risk_type is cost)
        q_waste = f"""
            SELECT SUM(r.estimated_savings_usd) 
            FROM recommendations r
            JOIN cloud_instances ci ON r.instance_id = ci.instance_id
            WHERE r.risk_type = 'cost' {provider_clause} {region_clause}
        """
        waste_res = conn.execute(q_waste, args_tuple).fetchone()[0]
        total_waste = float(waste_res) if waste_res is not None else 0.0

        # 5. Total Actionable Savings (sum across all recommendations)
        q_savings = f"""
            SELECT SUM(r.estimated_savings_usd) 
            FROM recommendations r
            JOIN cloud_instances ci ON r.instance_id = ci.instance_id
            WHERE 1=1 {provider_clause} {region_clause}
        """
        savings_res = conn.execute(q_savings, args_tuple).fetchone()[0]
        total_savings = float(savings_res) if savings_res is not None else 0.0

        # 6. Total Recommendations Count
        q_rec_count = f"""
            SELECT COUNT(*) 
            FROM recommendations r
            JOIN cloud_instances ci ON r.instance_id = ci.instance_id
            WHERE 1=1 {provider_clause} {region_clause}
        """
        rec_count = conn.execute(q_rec_count, args_tuple).fetchone()[0]

        return {
            "total_instances": total_inst,
            "critical_risk_count": critical_risk,
            "high_risk_count": high_risk,
            "total_monthly_waste_usd": total_waste,
            "total_potential_savings_usd": total_savings,
            "recommendation_count": rec_count
        }
    except Exception as e:
        print(f"Dashboard [Overview Metrics]: Error {e}")
        return {
            "total_instances": 0,
            "critical_risk_count": 0,
            "high_risk_count": 0,
            "total_monthly_waste_usd": 0.0,
            "total_potential_savings_usd": 0.0,
            "recommendation_count": 0
        }
    finally:
        if conn:
            conn.close()

@st.cache_data(ttl=300)
def get_risk_distribution(provider: Optional[str] = None, region: Optional[str] = None) -> pd.DataFrame:
    """
    Groups instances into Critical, High, Medium, and Low risk buckets matching
    the centralized operational risk semantics. Always guarantees all 4 tiers are present.
    """
    conn = None
    try:
        conn = get_read_only_conn()
        provider_clause = " AND ci.cloud_provider = ?" if provider and provider != "All" else ""
        region_clause = " AND ci.region = ?" if region and region != "All" else ""
        
        args = []
        if provider and provider != "All":
            args.append(provider)
        if region and region != "All":
            args.append(region)

        case_expr = get_risk_tier_sql_case("rs.overall_risk_score")
        query = f"""
            SELECT 
                {case_expr} AS risk_category,
                COUNT(*) AS count
            FROM risk_scores rs
            JOIN cloud_instances ci ON rs.instance_id = ci.instance_id
            WHERE 1=1 {provider_clause} {region_clause}
            GROUP BY risk_category
        """
        df = conn.execute(query, tuple(args)).fetchdf()
        
        # Ensure all tiers exist including Unknown even if count is 0
        all_tiers = pd.DataFrame({"risk_category": ["Critical", "High", "Medium", "Low", "Unknown"]})
        merged = pd.merge(all_tiers, df, on="risk_category", how="left").fillna(0)
        merged["count"] = merged["count"].astype(int)
        return merged
    except Exception as e:
        print(f"Dashboard [Risk Dist]: Error {e}")
        return pd.DataFrame({"risk_category": ["Critical", "High", "Medium", "Low", "Unknown"], "count": [0, 0, 0, 0, 0]})
    finally:
        if conn:
            conn.close()

@st.cache_data(ttl=300)
def get_cost_trend(days: int = 30, provider: Optional[str] = None, region: Optional[str] = None) -> pd.DataFrame:
    """
    Queries aggregate daily cost histories for the given day window, with optional provider and region filters.
    """
    conn = None
    try:
        conn = get_read_only_conn()
        provider_clause = " AND ci.cloud_provider = ?" if provider and provider != "All" else ""
        region_clause = " AND ci.region = ?" if region and region != "All" else ""
        
        args = []
        if provider and provider != "All":
            args.append(provider)
        if region and region != "All":
            args.append(region)
        args.append(days)

        query = f"""
            SELECT c.date, SUM(c.daily_cost_usd) AS daily_cost
            FROM cost_data c
            JOIN cloud_instances ci ON c.instance_id = ci.instance_id
            WHERE 1=1 {provider_clause} {region_clause}
            GROUP BY c.date
            ORDER BY c.date DESC
            LIMIT ?
        """
        df = conn.execute(query, tuple(args)).fetchdf()
        return df.sort_values(by="date", ascending=True)
    except Exception as e:
        print(f"Dashboard [Cost Trend]: Error {e}")
        return pd.DataFrame(columns=["date", "daily_cost"])
    finally:
        if conn:
            conn.close()

@st.cache_data(ttl=300)
def get_top_critical_instances(limit: int = 10, provider: Optional[str] = None, region: Optional[str] = None) -> pd.DataFrame:
    """
    Retrieves highest overall risk score instances with formatted operational tier and breakdown scores.
    """
    conn = None
    try:
        conn = get_read_only_conn()
        provider_clause = " AND ci.cloud_provider = ?" if provider and provider != "All" else ""
        region_clause = " AND ci.region = ?" if region and region != "All" else ""
        
        args = []
        if provider and provider != "All":
            args.append(provider)
        if region and region != "All":
            args.append(region)
        args.append(limit)

        case_expr = get_risk_tier_sql_case("rs.overall_risk_score")
        query = f"""
            SELECT 
                rs.instance_id, ci.cloud_provider, ci.instance_type, ci.region, 
                rs.security_risk_score, rs.anomaly_score, rs.cost_waste_score, rs.overall_risk_score,
                {case_expr} AS operational_tier
            FROM risk_scores rs
            JOIN cloud_instances ci ON rs.instance_id = ci.instance_id
            WHERE 1=1 {provider_clause} {region_clause}
            ORDER BY rs.overall_risk_score DESC
            LIMIT ?
        """
        df = conn.execute(query, tuple(args)).fetchdf()
        return df
    except Exception as e:
        print(f"Dashboard [Top Critical]: Error {e}")
        return pd.DataFrame(columns=[
            "instance_id", "cloud_provider", "instance_type", "region",
            "security_risk_score", "anomaly_score", "cost_waste_score", "overall_risk_score", "operational_tier"
        ])
    finally:
        if conn:
            conn.close()

@st.cache_data(ttl=300)
def get_risk_by_region(provider: Optional[str] = None) -> pd.DataFrame:
    """
    Queries average risk score grouped by provider and region.
    """
    conn = None
    try:
        conn = get_read_only_conn()
        provider_clause = " WHERE ci.cloud_provider = ?" if provider and provider != "All" else ""
        args = (provider,) if provider and provider != "All" else ()
        
        query = f"""
            SELECT ci.cloud_provider, ci.region, AVG(rs.overall_risk_score) AS avg_risk_score
            FROM risk_scores rs
            JOIN cloud_instances ci ON rs.instance_id = ci.instance_id
            {provider_clause}
            GROUP BY ci.cloud_provider, ci.region
            ORDER BY avg_risk_score DESC
        """
        df = conn.execute(query, args).fetchdf()
        return df
    except Exception as e:
        print(f"Dashboard [Region Risk]: Error {e}")
        return pd.DataFrame(columns=["cloud_provider", "region", "avg_risk_score"])
    finally:
        if conn:
            conn.close()

@st.cache_data(ttl=300)
def get_port_exposure(provider: Optional[str] = None, region: Optional[str] = None) -> pd.DataFrame:
    """
    Parses open_ports configurations across all fleet instances and compiles occurrence counts.
    """
    conn = None
    try:
        conn = get_read_only_conn()
        provider_clause = " AND ci.cloud_provider = ?" if provider and provider != "All" else ""
        region_clause = " AND ci.region = ?" if region and region != "All" else ""
        args = []
        if provider and provider != "All":
            args.append(provider)
        if region and region != "All":
            args.append(region)
            
        query = f"""
            SELECT sc.open_ports 
            FROM security_configurations sc
            JOIN cloud_instances ci ON sc.instance_id = ci.instance_id
            WHERE 1=1 {provider_clause} {region_clause}
        """
        df = conn.execute(query, tuple(args)).fetchdf()
        
        ports = []
        for p_str in df["open_ports"].dropna():
            for p in p_str.split(","):
                p_clean = p.strip()
                if p_clean:
                    ports.append(p_clean)
                    
        counts = Counter(ports)
        out_df = pd.DataFrame(counts.items(), columns=["port", "count"])
        return out_df.sort_values(by="count", ascending=False)
    except Exception as e:
        print(f"Dashboard [Port Exposure]: Error {e}")
        return pd.DataFrame(columns=["port", "count"])
    finally:
        if conn:
            conn.close()

@st.cache_data(ttl=300)
def get_vulnerability_breakdown(provider: Optional[str] = None, region: Optional[str] = None) -> pd.DataFrame:
    """
    Aggregates configuration vulnerability indicators across all fleet instances.
    """
    conn = None
    try:
        conn = get_read_only_conn()
        provider_clause = " AND ci.cloud_provider = ?" if provider and provider != "All" else ""
        region_clause = " AND ci.region = ?" if region and region != "All" else ""
        args = []
        if provider and provider != "All":
            args.append(provider)
        if region and region != "All":
            args.append(region)
            
        query = f"""
            SELECT 
                SUM(CASE WHEN sc.internet_exposed = TRUE THEN 1 ELSE 0 END) AS internet_exposed,
                SUM(CASE WHEN sc.encryption_enabled = FALSE THEN 1 ELSE 0 END) AS no_encryption,
                SUM(CASE WHEN sc.iam_permission_level = 'excessive' THEN 1 ELSE 0 END) AS excessive_iam,
                SUM(CASE WHEN sc.failed_logins_7d > 10 THEN 1 ELSE 0 END) AS brute_force_high
            FROM security_configurations sc
            JOIN cloud_instances ci ON sc.instance_id = ci.instance_id
            WHERE 1=1 {provider_clause} {region_clause}
        """
        df = conn.execute(query, tuple(args)).fetchdf()
        
        melted = pd.DataFrame({
            "vulnerability": ["Internet Exposed", "Excessive IAM", "Unencrypted Volume", "Brute-force attempts"],
            "count": [
                int(df["internet_exposed"].iloc[0]) if not df.empty and pd.notna(df["internet_exposed"].iloc[0]) else 0,
                int(df["excessive_iam"].iloc[0]) if not df.empty and pd.notna(df["excessive_iam"].iloc[0]) else 0,
                int(df["no_encryption"].iloc[0]) if not df.empty and pd.notna(df["no_encryption"].iloc[0]) else 0,
                int(df["brute_force_high"].iloc[0]) if not df.empty and pd.notna(df["brute_force_high"].iloc[0]) else 0
            ]
        })
        return melted
    except Exception as e:
        print(f"Dashboard [Vuln Breakdown]: Error {e}")
        return pd.DataFrame(columns=["vulnerability", "count"])
    finally:
        if conn:
            conn.close()

@st.cache_data(ttl=300)
def get_security_events_timeline(provider: Optional[str] = None, region: Optional[str] = None) -> pd.DataFrame:
    """
    Queries security logging events chronologically with optional provider and region filters.
    """
    conn = None
    try:
        conn = get_read_only_conn()
        provider_clause = " AND ci.cloud_provider = ?" if provider and provider != "All" else ""
        region_clause = " AND ci.region = ?" if region and region != "All" else ""
        args = []
        if provider and provider != "All":
            args.append(provider)
        if region and region != "All":
            args.append(region)
            
        query = f"""
            SELECT se.event_id, se.instance_id, se.event_type, se.severity, se.description, se.timestamp,
                   ci.cloud_provider, ci.region
            FROM security_events se
            JOIN cloud_instances ci ON se.instance_id = ci.instance_id
            WHERE 1=1 {provider_clause} {region_clause}
            ORDER BY se.timestamp ASC
        """
        df = conn.execute(query, tuple(args)).fetchdf()
        return df
    except Exception as e:
        print(f"Dashboard [Events Timeline]: Error {e}")
        return pd.DataFrame(columns=["event_id", "instance_id", "event_type", "severity", "description", "timestamp", "cloud_provider", "region"])
    finally:
        if conn:
            conn.close()

@st.cache_data(ttl=300)
def get_cost_by_instance_type(provider: Optional[str] = None, region: Optional[str] = None) -> pd.DataFrame:
    """
    Aggregates 30-day spend grouped by instance size across all fleet instances.
    """
    conn = None
    try:
        conn = get_read_only_conn()
        provider_clause = " AND ci.cloud_provider = ?" if provider and provider != "All" else ""
        region_clause = " AND ci.region = ?" if region and region != "All" else ""
        args = []
        if provider and provider != "All":
            args.append(provider)
        if region and region != "All":
            args.append(region)
            
        query = f"""
            SELECT ci.instance_type, SUM(c.daily_cost_usd) AS monthly_cost, SUM(c.daily_cost_usd) AS total_cost
            FROM cost_data c
            JOIN cloud_instances ci ON c.instance_id = ci.instance_id
            WHERE c.date >= (SELECT MAX(date) - INTERVAL 29 DAYS FROM cost_data)
              {provider_clause} {region_clause}
            GROUP BY ci.instance_type
            ORDER BY monthly_cost DESC
        """
        df = conn.execute(query, tuple(args)).fetchdf()
        return df
    except Exception as e:
        print(f"Dashboard [Cost Type]: Error {e}")
        return pd.DataFrame(columns=["instance_type", "monthly_cost", "total_cost"])
    finally:
        if conn:
            conn.close()

@st.cache_data(ttl=300)
def get_fleet_spend_breakdown(provider: Optional[str] = None, region: Optional[str] = None) -> pd.DataFrame:
    """
    Retrieves true fleet-wide monthly spend (last 30 days) and total actionable waste/savings.
    """
    conn = None
    try:
        conn = get_read_only_conn()
        provider_clause = " AND ci.cloud_provider = ?" if provider and provider != "All" else ""
        region_clause = " AND ci.region = ?" if region and region != "All" else ""
        args = []
        if provider and provider != "All":
            args.append(provider)
        if region and region != "All":
            args.append(region)
        args_tuple = tuple(args)

        q_spend = f"""
            SELECT SUM(c.daily_cost_usd) 
            FROM cost_data c
            JOIN cloud_instances ci ON c.instance_id = ci.instance_id
            WHERE c.date >= (SELECT MAX(date) - INTERVAL 29 DAYS FROM cost_data)
              {provider_clause} {region_clause}
        """
        spend_res = conn.execute(q_spend, args_tuple).fetchone()[0]
        total_monthly_spend = float(spend_res) if spend_res is not None else 0.0

        q_savings = f"""
            SELECT SUM(r.estimated_savings_usd)
            FROM recommendations r
            JOIN cloud_instances ci ON r.instance_id = ci.instance_id
            WHERE 1=1 {provider_clause} {region_clause}
        """
        savings_res = conn.execute(q_savings, args_tuple).fetchone()[0]
        wasted_spend = float(savings_res) if savings_res is not None else 0.0

        return pd.DataFrame([{
            "total_monthly_spend": total_monthly_spend,
            "wasted_spend": wasted_spend,
            "utilized_spend": max(0.0, total_monthly_spend - wasted_spend)
        }])
    except Exception as e:
        print(f"Dashboard [Fleet Spend Breakdown]: Error {e}")
        return pd.DataFrame([{"total_monthly_spend": 0.0, "wasted_spend": 0.0, "utilized_spend": 0.0}])
    finally:
        if conn:
            conn.close()

@st.cache_data(ttl=300)
def get_wasteful_instances(limit: int = 20, provider: Optional[str] = None, region: Optional[str] = None) -> pd.DataFrame:
    """
    Rank instances by cost waste score, projecting monthly metrics and potential savings.
    """
    conn = None
    try:
        conn = get_read_only_conn()
        provider_clause = " AND ci.cloud_provider = ?" if provider and provider != "All" else ""
        region_clause = " AND ci.region = ?" if region and region != "All" else ""
        args = []
        if provider and provider != "All":
            args.append(provider)
        if region and region != "All":
            args.append(region)
        args.append(limit)

        query = f"""
            SELECT 
                rs.instance_id, 
                ci.cloud_provider,
                ci.instance_type,
                ci.region,
                AVG(cd.utilization_pct) AS avg_utilization,
                (AVG(cd.daily_cost_usd) * 30) AS monthly_cost,
                CASE 
                    WHEN rs.cost_waste_score >= 60.0 THEN (AVG(cd.daily_cost_usd) * 30) * 0.75
                    ELSE 0.0
                END AS estimated_savings,
                rs.cost_waste_score
            FROM risk_scores rs
            JOIN cloud_instances ci ON rs.instance_id = ci.instance_id
            JOIN cost_data cd ON rs.instance_id = cd.instance_id
            WHERE 1=1 {provider_clause} {region_clause}
            GROUP BY rs.instance_id, ci.cloud_provider, ci.instance_type, ci.region, rs.cost_waste_score
            ORDER BY rs.cost_waste_score DESC
            LIMIT ?
        """
        df = conn.execute(query, tuple(args)).fetchdf()
        return df
    except Exception as e:
        print(f"Dashboard [Wasteful Instances]: Error {e}")
        return pd.DataFrame(columns=["instance_id", "cloud_provider", "instance_type", "region", "avg_utilization", "monthly_cost", "estimated_savings", "cost_waste_score"])
    finally:
        if conn:
            conn.close()

@st.cache_data(ttl=300)
def get_utilization_scatter_data(provider: Optional[str] = None, region: Optional[str] = None) -> pd.DataFrame:
    """
    Collects 2D utilization scatter parameters across all instances.
    """
    conn = None
    try:
        conn = get_read_only_conn()
        provider_clause = " AND ci.cloud_provider = ?" if provider and provider != "All" else ""
        region_clause = " AND ci.region = ?" if region and region != "All" else ""
        args = []
        if provider and provider != "All":
            args.append(provider)
        if region and region != "All":
            args.append(region)

        query = f"""
            SELECT 
                m.instance_id,
                ci.cloud_provider,
                ci.instance_type,
                ci.region,
                AVG(m.cpu_utilization_pct) AS avg_cpu_utilization_pct,
                AVG(m.memory_utilization_pct) AS avg_memory_utilization_pct,
                AVG(c.daily_cost_usd) AS avg_daily_cost_usd,
                rs.overall_risk_score
            FROM metrics_daily m
            JOIN cost_data c ON m.instance_id = c.instance_id AND m.date = c.date
            JOIN risk_scores rs ON m.instance_id = rs.instance_id
            JOIN cloud_instances ci ON m.instance_id = ci.instance_id
            WHERE 1=1 {provider_clause} {region_clause}
            GROUP BY m.instance_id, ci.cloud_provider, ci.instance_type, ci.region, rs.overall_risk_score
        """
        df = conn.execute(query, tuple(args)).fetchdf()
        return df
    except Exception as e:
        print(f"Dashboard [Scatter Data]: Error {e}")
        return pd.DataFrame(columns=["instance_id", "cloud_provider", "instance_type", "region", "avg_cpu_utilization_pct", "avg_memory_utilization_pct", "avg_daily_cost_usd", "overall_risk_score"])
    finally:
        if conn:
            conn.close()

@st.cache_data(ttl=300)
def get_recommendations(priority_filter: Optional[str] = None, status_filter: Optional[str] = None) -> pd.DataFrame:
    """
    Loads recommendations from database with optional priority and status filters.
    Includes linked instance metadata (cloud_provider, region, instance_type).
    """
    conn = None
    try:
        conn = get_read_only_conn()
        query = """
            SELECT r.*, ci.cloud_provider, ci.region, ci.instance_type
            FROM recommendations r
            LEFT JOIN cloud_instances ci ON r.instance_id = ci.instance_id
            WHERE 1=1
        """
        args = []
        
        if priority_filter and priority_filter != "All":
            query += " AND r.priority = ?"
            args.append(priority_filter)
            
        if status_filter and status_filter != "All":
            query += " AND r.status = ?"
            args.append(status_filter.lower())
            
        query += " ORDER BY r.priority = 'Critical' DESC, r.priority = 'High' DESC, r.priority = 'Medium' DESC, r.estimated_savings_usd DESC"
        
        df = conn.execute(query, tuple(args)).fetchdf()

        # Schema backward-compatibility
        if "generation_source" not in df.columns:
            df["generation_source"] = "legacy_unknown"
        if "model_name" not in df.columns:
            df["model_name"] = "unknown"
        if "fallback_reason" not in df.columns:
            df["fallback_reason"] = "pre_migration_record"
        if "expected_benefit" not in df.columns:
            df["expected_benefit"] = None

        return df
    except Exception as e:
        print(f"Dashboard [Recommendations]: Error {e}")
        return pd.DataFrame(columns=[
            "recommendation_id", "instance_id", "risk_type", "priority", "title",
            "description", "implementation_steps", "estimated_savings_usd",
            "estimated_effort_hours", "status", "generated_at",
            "generation_source", "model_name", "fallback_reason", "expected_benefit",
            "cloud_provider", "region", "instance_type"
        ])
    finally:
        if conn:
            conn.close()

@st.cache_data(ttl=300)
def get_all_security_configs(provider: Optional[str] = None, region: Optional[str] = None) -> pd.DataFrame:
    """
    Retrieves all instances along with their detailed security configuration parameters.
    """
    conn = None
    try:
        conn = get_read_only_conn()
        provider_clause = " AND ci.cloud_provider = ?" if provider and provider != "All" else ""
        region_clause = " AND ci.region = ?" if region and region != "All" else ""
        args = []
        if provider and provider != "All":
            args.append(provider)
        if region and region != "All":
            args.append(region)
            
        query = f"""
            SELECT sc.instance_id, ci.cloud_provider, ci.region, sc.open_ports, 
                   sc.internet_exposed, sc.encryption_enabled, sc.iam_permission_level, 
                   sc.failed_logins_7d, sc.last_patch_date
            FROM security_configurations sc
            JOIN cloud_instances ci ON sc.instance_id = ci.instance_id
            WHERE 1=1 {provider_clause} {region_clause}
            ORDER BY sc.internet_exposed DESC, sc.failed_logins_7d DESC
        """
        df = conn.execute(query, tuple(args)).fetchdf()
        return df
    except Exception as e:
        print(f"Dashboard [All Sec Configs]: Error {e}")
        return pd.DataFrame(columns=["instance_id", "cloud_provider", "region", "open_ports", "internet_exposed", "encryption_enabled", "iam_permission_level", "failed_logins_7d", "last_patch_date"])
    finally:
        if conn:
            conn.close()

@st.cache_data(ttl=300)
def get_audit_metadata() -> dict:
    """
    Retrieves system, warehouse, and model execution metadata counts and timestamps.
    """
    conn = None
    try:
        conn = get_read_only_conn()
        total_inst = conn.execute("SELECT COUNT(*) FROM cloud_instances").fetchone()[0]
        total_metrics = conn.execute("SELECT COUNT(*) FROM metrics_daily").fetchone()[0]
        calc_time = conn.execute("SELECT MAX(calculated_at) FROM risk_scores").fetchone()[0]
        gen_time = conn.execute("SELECT MAX(generated_at) FROM recommendations").fetchone()[0]
        rec_count = conn.execute("SELECT COUNT(*) FROM recommendations").fetchone()[0]
        
        try:
            sources = [r[0] for r in conn.execute("SELECT DISTINCT generation_source FROM recommendations").fetchall() if r[0]]
        except Exception:
            sources = []

        calc_time_str = calc_time.strftime("%Y-%m-%d %H:%M:%S") if calc_time else "Data Unavailable"
        gen_time_str = gen_time.strftime("%Y-%m-%d %H:%M:%S") if gen_time else "Data Unavailable"
        
        return {
            "total_instances": total_inst,
            "total_metrics_records": total_metrics,
            "calc_time_str": calc_time_str,
            "gen_time_str": gen_time_str,
            "recommendation_count": rec_count,
            "generation_sources": sources,
            "db_status": "Connected (DuckDB)",
            "db_path": DB_PATH
        }
    except Exception as e:
        print(f"Dashboard [Audit Metadata]: Error {e}")
        return {
            "total_instances": 0,
            "total_metrics_records": 0,
            "calc_time_str": "Data Unavailable",
            "gen_time_str": "Data Unavailable",
            "recommendation_count": 0,
            "generation_sources": [],
            "db_status": "Disconnected",
            "db_path": DB_PATH
        }
    finally:
        if conn:
            conn.close()

def update_recommendation_status(recommendation_id: str, new_status: str):
    """
    Modifies recommendations status using a separate write connection.
    Clears cache to force instant interface updates.
    """
    print(f"Dashboard [Data Access]: Modifying {recommendation_id} status to '{new_status}'...")
    exists, path = check_db_exists()
    if not exists:
        return
        
    try:
        conn = duckdb.connect(path)
        conn.execute(
            "UPDATE recommendations SET status = ? WHERE recommendation_id = ?",
            (new_status.lower(), recommendation_id)
        )
        conn.close()
        st.cache_data.clear()
    except Exception as e:
        print(f"Dashboard [Data Access]: Write update failed ({e})")
