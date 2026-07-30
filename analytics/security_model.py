import pandas as pd
from warehouse.db_connection import get_connection

class SecurityRiskModel:
    """
    Rule-based Security Risk scoring system for CLARA.

    RATIONALE:
    Security risk in this dataset has no historical ground-truth labels (we are not predicting
    from past breach outcomes). Therefore, a transparent, auditable weighted-rule model is
    more appropriate and explainable than an unsupervised or supervised black box for this
    specific sub-problem. This allows non-technical evaluators, finance managers, and security
    administrators to clearly understand exactly why an instance has been flagged as high risk.
    """
    def __init__(self):
        pass

    def calculate_risk(self, conn) -> pd.DataFrame:
        """
        Queries security configurations joined with cloud instances, calculates a risk score
        capped at 100 based on configuration vulnerability factors, and details contributing logs.

        Parameters:
            conn (duckdb.DuckDBPyConnection): Active DuckDB connection.

        Returns:
            pd.DataFrame: Columns [instance_id, security_risk_score, contributing_factors].
        """
        query = """
            SELECT sc.*, ci.cloud_provider, ci.status
            FROM security_configurations sc
            JOIN cloud_instances ci ON sc.instance_id = ci.instance_id
        """
        df = conn.execute(query).fetchdf()
        
        results = []
        for _, row in df.iterrows():
            score = 0
            factors = []
            
            # Factor 1: Internet exposure
            if row["internet_exposed"]:
                score += 40
                factors.append("internet_exposed")
                
            # Factor 2: Storage encryption
            if not row["encryption_enabled"]:
                score += 25
                factors.append("no_encryption")
                
            # Factor 3: IAM permission level
            iam = row["iam_permission_level"]
            if iam == "excessive":
                score += 20
                factors.append("excessive_iam")
            elif iam == "standard":
                score += 5
                factors.append("standard_iam")
                
            # Factor 4: Failed login attempts in 7 days
            logins = row["failed_logins_7d"]
            if logins > 10:
                score += 15
                factors.append("brute_force_high")
            elif 4 <= logins <= 10:
                score += 5
                factors.append("brute_force_medium")
                
            # Factor 5: Exposed remote access port bonus
            ports = str(row["open_ports"])
            has_remote_ports = "22" in ports or "3389" in ports
            if has_remote_ports and row["internet_exposed"]:
                score += 10
                factors.append("remote_access_exposed")
                
            # Cap total security risk score at 100
            final_score = min(score, 100)
            factors_str = ",".join(factors) if factors else "none"
            
            results.append({
                "instance_id": row["instance_id"],
                "security_risk_score": float(final_score),
                "contributing_factors": factors_str
            })
            
        return pd.DataFrame(results)

if __name__ == "__main__":
    conn = get_connection()
    model = SecurityRiskModel()
    scores = model.calculate_risk(conn)
    print(scores.head())
    conn.close()
