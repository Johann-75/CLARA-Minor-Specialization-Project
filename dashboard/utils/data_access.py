import os
from collections import Counter
import streamlit as st
import pandas as pd
import duckdb

DB_PATH = "clara.db"

def check_db_exists():
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
            # Fallback if run outside of Streamlit (e.g. pytest)
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
def get_overview_metrics() -> dict:
    """
    Queries overall metrics aggregates.
    """
    conn = None
    try:
        conn = get_read_only_conn()
        
        total_inst = conn.execute("SELECT COUNT(*) FROM cloud_instances").fetchone()[0]
        critical_risk = conn.execute("SELECT COUNT(*) FROM risk_scores WHERE overall_risk_score > 70").fetchone()[0]
        
        # Monthly waste: sum of savings where risk_type is cost
        waste_res = conn.execute("SELECT SUM(estimated_savings_usd) FROM recommendations WHERE risk_type = 'cost'").fetchone()[0]
        total_waste = float(waste_res) if waste_res is not None else 0.0
        
        # Total potential savings: sum of all recommendations savings
        savings_res = conn.execute("SELECT SUM(estimated_savings_usd) FROM recommendations").fetchone()[0]
        total_savings = float(savings_res) if savings_res is not None else 0.0
        
        return {
            "total_instances": total_inst,
            "critical_risk_count": critical_risk,
            "total_monthly_waste_usd": total_waste,
            "total_potential_savings_usd": total_savings
        }
    except Exception as e:
        print(f"Dashboard [Overview Metrics]: Error {e}")
        return {
            "total_instances": 0,
            "critical_risk_count": 0,
            "total_monthly_waste_usd": 0.0,
            "total_potential_savings_usd": 0.0
        }
    finally:
        if conn:
            conn.close()

@st.cache_data(ttl=300)
def get_risk_distribution() -> pd.DataFrame:
    """
    Groups instances into Critical, High, Medium, and Low risk buckets.
    """
    conn = None
    try:
        conn = get_read_only_conn()
        query = """
            SELECT 
                CASE 
                    WHEN overall_risk_score >= 80 THEN 'Critical'
                    WHEN overall_risk_score >= 60 THEN 'High'
                    WHEN overall_risk_score >= 40 THEN 'Medium'
                    ELSE 'Low'
                END AS risk_category,
                COUNT(*) AS count
            FROM risk_scores
            GROUP BY risk_category
        """
        df = conn.execute(query).fetchdf()
        return df
    except Exception as e:
        print(f"Dashboard [Risk Dist]: Error {e}")
        return pd.DataFrame(columns=["risk_category", "count"])
    finally:
        if conn:
            conn.close()

@st.cache_data(ttl=300)
def get_cost_trend(days=30) -> pd.DataFrame:
    """
    Queries aggregate daily cost histories.
    """
    conn = None
    try:
        conn = get_read_only_conn()
        query = """
            SELECT date, SUM(daily_cost_usd) AS daily_cost
            FROM cost_data
            GROUP BY date
            ORDER BY date DESC
            LIMIT ?
        """
        df = conn.execute(query, (days,)).fetchdf()
        # Sort chronologically for charting
        return df.sort_values(by="date", ascending=True)
    except Exception as e:
        print(f"Dashboard [Cost Trend]: Error {e}")
        return pd.DataFrame(columns=["date", "daily_cost"])
    finally:
        if conn:
            conn.close()

@st.cache_data(ttl=300)
def get_top_critical_instances(limit=10) -> pd.DataFrame:
    """
    Retrieves highest overall risk score instances.
    """
    conn = None
    try:
        conn = get_read_only_conn()
        query = """
            SELECT 
                rs.instance_id, ci.cloud_provider, ci.instance_type, ci.region, 
                rs.security_risk_score, rs.anomaly_score, rs.cost_waste_score, rs.overall_risk_score
            FROM risk_scores rs
            JOIN cloud_instances ci ON rs.instance_id = ci.instance_id
            ORDER BY rs.overall_risk_score DESC
            LIMIT ?
        """
        df = conn.execute(query, (limit,)).fetchdf()
        return df
    except Exception as e:
        print(f"Dashboard [Top Critical]: Error {e}")
        return pd.DataFrame(columns=["instance_id", "cloud_provider", "instance_type", "region", "security_risk_score", "anomaly_score", "cost_waste_score", "overall_risk_score"])
    finally:
        if conn:
            conn.close()

@st.cache_data(ttl=300)
def get_risk_by_region() -> pd.DataFrame:
    """
    Queries average risk score grouped by provider and region.
    """
    conn = None
    try:
        conn = get_read_only_conn()
        query = """
            SELECT ci.cloud_provider, ci.region, AVG(rs.overall_risk_score) AS avg_risk_score
            FROM risk_scores rs
            JOIN cloud_instances ci ON rs.instance_id = ci.instance_id
            GROUP BY ci.cloud_provider, ci.region
        """
        df = conn.execute(query).fetchdf()
        return df
    except Exception as e:
        print(f"Dashboard [Region Risk]: Error {e}")
        return pd.DataFrame(columns=["cloud_provider", "region", "avg_risk_score"])
    finally:
        if conn:
            conn.close()

@st.cache_data(ttl=300)
def get_port_exposure() -> pd.DataFrame:
    """
    Parses open_ports configurations and compiles occurrence counts.
    """
    conn = None
    try:
        conn = get_read_only_conn()
        df = conn.execute("SELECT open_ports FROM security_configurations").fetchdf()
        
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
def get_vulnerability_breakdown() -> pd.DataFrame:
    """
    Aggregates metrics configuration flags.
    """
    conn = None
    try:
        conn = get_read_only_conn()
        query = """
            SELECT 
                SUM(CASE WHEN internet_exposed = TRUE THEN 1 ELSE 0 END) AS internet_exposed,
                SUM(CASE WHEN encryption_enabled = FALSE THEN 1 ELSE 0 END) AS no_encryption,
                SUM(CASE WHEN iam_permission_level = 'excessive' THEN 1 ELSE 0 END) AS excessive_iam,
                SUM(CASE WHEN failed_logins_7d > 10 THEN 1 ELSE 0 END) AS brute_force_high
            FROM security_configurations
        """
        df = conn.execute(query).fetchdf()
        
        melted = pd.DataFrame({
            "vulnerability": ["Internet Exposed", "Unencrypted Volume", "Excessive IAM", "Brute-force attempts"],
            "count": [
                int(df["internet_exposed"].iloc[0]) if not df.empty else 0,
                int(df["no_encryption"].iloc[0]) if not df.empty else 0,
                int(df["excessive_iam"].iloc[0]) if not df.empty else 0,
                int(df["brute_force_high"].iloc[0]) if not df.empty else 0
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
def get_security_events_timeline() -> pd.DataFrame:
    """
    Queries all security logging events chronologically.
    """
    conn = None
    try:
        conn = get_read_only_conn()
        df = conn.execute("SELECT * FROM security_events ORDER BY timestamp ASC").fetchdf()
        return df
    except Exception as e:
        print(f"Dashboard [Events Timeline]: Error {e}")
        return pd.DataFrame(columns=["event_id", "instance_id", "event_type", "severity", "description", "timestamp"])
    finally:
        if conn:
            conn.close()

@st.cache_data(ttl=300)
def get_cost_by_instance_type() -> pd.DataFrame:
    """
    Aggregates daily cost group by instance size type.
    """
    conn = None
    try:
        conn = get_read_only_conn()
        query = """
            SELECT ci.instance_type, SUM(c.daily_cost_usd) AS total_cost
            FROM cost_data c
            JOIN cloud_instances ci ON c.instance_id = ci.instance_id
            GROUP BY ci.instance_type
        """
        df = conn.execute(query).fetchdf()
        return df
    except Exception as e:
        print(f"Dashboard [Cost Type]: Error {e}")
        return pd.DataFrame(columns=["instance_type", "total_cost"])
    finally:
        if conn:
            conn.close()

@st.cache_data(ttl=300)
def get_wasteful_instances(limit=20) -> pd.DataFrame:
    """
    Rank instances by cost waste score, projecting monthly metrics and potential savings.
    """
    conn = None
    try:
        conn = get_read_only_conn()
        query = """
            SELECT 
                rs.instance_id, 
                ci.instance_type,
                AVG(cd.utilization_pct) AS avg_utilization,
                (AVG(cd.daily_cost_usd) * 30) AS monthly_cost,
                CASE 
                    WHEN rs.cost_waste_score >= 70.0 THEN (AVG(cd.daily_cost_usd) * 30) * 0.9
                    ELSE 0.0
                END AS estimated_savings
            FROM risk_scores rs
            JOIN cloud_instances ci ON rs.instance_id = ci.instance_id
            JOIN cost_data cd ON rs.instance_id = cd.instance_id
            GROUP BY rs.instance_id, ci.instance_type, rs.cost_waste_score
            ORDER BY rs.cost_waste_score DESC
            LIMIT ?
        """
        df = conn.execute(query, (limit,)).fetchdf()
        return df
    except Exception as e:
        print(f"Dashboard [Wasteful Instances]: Error {e}")
        return pd.DataFrame(columns=["instance_id", "instance_type", "avg_utilization", "monthly_cost", "estimated_savings"])
    finally:
        if conn:
            conn.close()

@st.cache_data(ttl=300)
def get_utilization_scatter_data() -> pd.DataFrame:
    """
    Collects 2D utilization scatter parameters.
    """
    conn = None
    try:
        conn = get_read_only_conn()
        query = """
            SELECT 
                m.instance_id,
                AVG(m.cpu_utilization_pct) AS avg_cpu_utilization_pct,
                AVG(m.memory_utilization_pct) AS avg_memory_utilization_pct,
                AVG(c.daily_cost_usd) AS avg_daily_cost_usd,
                rs.overall_risk_score
            FROM metrics_daily m
            JOIN cost_data c ON m.instance_id = c.instance_id AND m.date = c.date
            JOIN risk_scores rs ON m.instance_id = rs.instance_id
            GROUP BY m.instance_id, rs.overall_risk_score
        """
        df = conn.execute(query).fetchdf()
        return df
    except Exception as e:
        print(f"Dashboard [Scatter Data]: Error {e}")
        return pd.DataFrame(columns=["instance_id", "avg_cpu_utilization_pct", "avg_memory_utilization_pct", "avg_daily_cost_usd", "overall_risk_score"])
    finally:
        if conn:
            conn.close()

@st.cache_data(ttl=300)
def get_recommendations(priority_filter=None, status_filter=None) -> pd.DataFrame:
    """
    Loads recommendations from database with optional filters.
    """
    conn = None
    try:
        conn = get_read_only_conn()
        query = "SELECT * FROM recommendations WHERE 1=1"
        args = []
        
        if priority_filter and priority_filter != "All":
            query += " AND priority = ?"
            args.append(priority_filter)
            
        if status_filter and status_filter != "All":
            query += " AND status = ?"
            args.append(status_filter.lower())
            
        if args:
            df = conn.execute(query, tuple(args)).fetchdf()
        else:
            df = conn.execute(query).fetchdf()
        return df
    except Exception as e:
        print(f"Dashboard [Recommendations]: Error {e}")
        return pd.DataFrame(columns=["recommendation_id", "instance_id", "risk_type", "priority", "title", "description", "implementation_steps", "estimated_savings_usd", "estimated_effort_hours", "status", "generated_at"])
    finally:
        if conn:
            conn.close()

@st.cache_data(ttl=300)
def get_all_security_configs() -> pd.DataFrame:
    """
    Retrieves all instances along with their detailed security configuration parameters.
    """
    conn = None
    try:
        conn = get_read_only_conn()
        df = conn.execute("SELECT * FROM security_configurations").fetchdf()
        return df
    except Exception as e:
        print(f"Dashboard [All Sec Configs]: Error {e}")
        return pd.DataFrame(columns=["instance_id", "open_ports", "internet_exposed", "encryption_enabled", "iam_permission_level", "failed_logins_7d", "last_patch_date"])
    finally:
        if conn:
            conn.close()

@st.cache_data(ttl=300)
def get_audit_metadata() -> dict:
    """
    Retrieves system and pipeline metadata counts and timestamps.
    """
    conn = None
    try:
        conn = get_read_only_conn()
        total_inst = conn.execute("SELECT COUNT(*) FROM cloud_instances").fetchone()[0]
        calc_time = conn.execute("SELECT MAX(calculated_at) FROM risk_scores").fetchone()[0]
        gen_time = conn.execute("SELECT MAX(generated_at) FROM recommendations").fetchone()[0]
        rec_count = conn.execute("SELECT COUNT(*) FROM recommendations").fetchone()[0]
        
        calc_time_str = calc_time.strftime("%Y-%m-%d %H:%M:%S") if calc_time else "Data Unavailable"
        gen_time_str = gen_time.strftime("%Y-%m-%d %H:%M:%S") if gen_time else "Data Unavailable"
        
        return {
            "total_instances": total_inst,
            "calc_time_str": calc_time_str,
            "gen_time_str": gen_time_str,
            "recommendation_count": rec_count
        }
    except Exception as e:
        print(f"Dashboard [Audit Metadata]: Error {e}")
        return {
            "total_instances": 0,
            "calc_time_str": "Data Unavailable",
            "gen_time_str": "Data Unavailable",
            "recommendation_count": 0
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
        
        # Clear Streamlit cache to force dashboard queries to pick up the changes
        st.cache_data.clear()
        
    except Exception as e:
        print(f"Dashboard [Data Access]: Write update failed ({e})")
