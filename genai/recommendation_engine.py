import uuid
import json
from datetime import datetime
import pandas as pd
import config
from genai.gemini_client import GeminiClient
from warehouse.db_connection import get_connection

class RecommendationEngine:
    """
    Recommendation engine querying high-risk instances and generating
    actionable security, cost, or anomaly recommendations using Gemini.
    """
    def __init__(self):
        self.client = GeminiClient()

    def _build_system_prompt(self, risk_type: str) -> str:
        """
        Builds the expert system prompt based on risk_type.
        """
        role_map = {
            "security": "cloud security governance",
            "cost": "cloud financial operations (FinOps) cost optimization",
            "anomaly": "cloud reliability engineering and operations"
        }
        role = role_map.get(risk_type, "cloud systems")
        
        prompt = f"""
        You are an expert in {role}. Your job is to analyze the provided cloud instance telemetry and risk metrics, and generate ONE specific, actionable recommendation to mitigate the risk.
        
        You must return ONLY a valid JSON object matching this exact schema:
        {{
          "title": "string, max 10 words, specific and actionable",
          "description": "string, 2-3 sentences explaining the issue in business terms, referencing the specific contributing factors given",
          "priority": "Critical" | "High" | "Medium" | "Low",
          "implementation_steps": ["step 1", "step 2", "step 3"],
          "estimated_effort_hours": number,
          "estimated_downtime_minutes": number
        }}
        
        Constraints:
        - Never invent facts, port numbers, or configuration flags not present in the provided instance data.
        - Keep the description grounded strictly in the numeric risk scores and contributing factors provided.
        - Do not wrap the JSON output in markdown blocks or explain it.
        """
        return prompt.strip()

    def _build_user_prompt(self, instance_row: dict, risk_type: str) -> str:
        """
        Formats instance parameters to build the user query prompt.
        """
        # Calculate contributing factors dynamically
        factors = []
        if instance_row.get("internet_exposed"):
            factors.append("internet_exposed")
        if not instance_row.get("encryption_enabled"):
            factors.append("no_encryption")
        if instance_row.get("iam_permission_level") == "excessive":
            factors.append("excessive_iam")
        elif instance_row.get("iam_permission_level") == "standard":
            factors.append("standard_iam")
        if instance_row.get("failed_logins_7d", 0) > 10:
            factors.append("brute_force_high")
        elif 4 <= instance_row.get("failed_logins_7d", 0) <= 10:
            factors.append("brute_force_medium")
            
        ports = str(instance_row.get("open_ports", ""))
        has_remote = "22" in ports or "3389" in ports
        if has_remote and instance_row.get("internet_exposed"):
            factors.append("remote_access_exposed")
            
        factors_str = ", ".join(factors) if factors else "none"
        monthly_cost = float(instance_row.get("daily_cost_usd", 0.0) * 30.0)
        cpu_util = float(instance_row.get("utilization_pct", 0.0))

        prompt = f"""
        Instance: {instance_row['instance_id']}
        Cloud Provider: {instance_row['cloud_provider']} | Region: {instance_row['region']} | Type: {instance_row['instance_type']}
        Security Risk Score: {instance_row['security_risk_score']}/100
        Anomaly Score: {instance_row['anomaly_score']}/100
        Cost Waste Score: {instance_row['cost_waste_score']}/100
        Contributing Factors: {factors_str}
        Monthly Cost: ${monthly_cost:.2f}
        Utilization: {cpu_util:.2f}% average CPU
        
        Generate ONE recommendation addressing the {risk_type} risk described above.
        """
        return prompt.strip()

    def generate_recommendation(self, instance_row: dict, risk_type: str) -> dict:
        """
        Invokes system prompts and Gemini JSON generation layers for an instance.
        """
        sys_prompt = self._build_system_prompt(risk_type)
        user_prompt = self._build_user_prompt(instance_row, risk_type)
        
        rec = self.client.generate_json(sys_prompt, user_prompt)
        
        # Inject standard required metadata keys
        rec["risk_type"] = risk_type
        rec["instance_id"] = instance_row["instance_id"]
        
        # Calculate estimated savings if cost_waste_score is high, regardless of dominant risk type
        if instance_row.get("cost_waste_score", 0.0) >= 70.0:
            rec["estimated_savings_usd"] = float(instance_row.get("daily_cost_usd", 0.0) * 30.0 * 0.9)
        else:
            rec["estimated_savings_usd"] = 0.0
            
        return rec

    def generate_for_all_high_risk(self, conn, threshold: float = None) -> list[dict]:
        """
        Queries high risk instances and generates recommendations for their dominant risk type.
        """
        if threshold is None:
            threshold = config.RECOMMENDATION_THRESHOLD
        # Select latest cost_data records only
        query = """
            SELECT 
                rs.instance_id, rs.anomaly_score, rs.security_risk_score, rs.cost_waste_score, rs.overall_risk_score,
                ci.cloud_provider, ci.region, ci.instance_type,
                sc.open_ports, sc.internet_exposed, sc.encryption_enabled, sc.iam_permission_level, sc.failed_logins_7d,
                cd.daily_cost_usd, cd.utilization_pct
            FROM risk_scores rs
            JOIN cloud_instances ci ON rs.instance_id = ci.instance_id
            JOIN security_configurations sc ON rs.instance_id = sc.instance_id
            JOIN cost_data cd ON rs.instance_id = cd.instance_id
            WHERE cd.date = (SELECT MAX(date) FROM cost_data)
              AND rs.overall_risk_score > ?
            ORDER BY rs.overall_risk_score DESC
        """
        
        df = conn.execute(query, (threshold,)).fetchdf()
        
        if df.empty:
            return []

        recommendations = []
        total = len(df)
        
        for idx, (_, row) in enumerate(df.iterrows(), 1):
            inst_id = row["instance_id"]
            
            # Determine dominant risk type
            sec = row["security_risk_score"]
            anom = row["anomaly_score"]
            cost = row["cost_waste_score"]
            
            if sec >= anom and sec >= cost:
                risk_type = "security"
            elif anom >= cost:
                risk_type = "anomaly"
            else:
                risk_type = "cost"
                
            print(f"GenAI [Recommendations]: Generating recommendation {idx}/{total} for {inst_id} (Type: {risk_type})...")
            
            rec = self.generate_recommendation(row.to_dict(), risk_type)
            recommendations.append(rec)
            
        return recommendations

    def save_recommendations(self, conn, recommendations: list[dict]):
        """
        Saves recommendation list to database recommendations table after truncation.
        """
        print("GenAI [Recommendations]: Truncating existing recommendation records...")
        conn.execute("DELETE FROM recommendations")
        
        if not recommendations:
            print("GenAI [Recommendations]: No recommendations to insert.")
            return

        print(f"GenAI [Recommendations]: Ingesting {len(recommendations)} recommendations...")
        
        insert_query = """
            INSERT INTO recommendations (
                recommendation_id, instance_id, risk_type, priority, title,
                description, implementation_steps, estimated_savings_usd,
                estimated_effort_hours, status, generated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        for rec in recommendations:
            rec_id = str(uuid.uuid4())
            steps = rec.get("implementation_steps", [])
            steps_str = " | ".join(steps) if isinstance(steps, list) else str(steps)
            
            conn.execute(insert_query, (
                rec_id,
                rec["instance_id"],
                rec["risk_type"],
                rec["priority"],
                rec["title"],
                rec["description"],
                steps_str,
                float(rec.get("estimated_savings_usd", 0.0)),
                float(rec.get("estimated_effort_hours", 1.0)),
                "pending",
                datetime.now()
            ))
            
        print("GenAI [Recommendations]: Ingestion complete.")

if __name__ == "__main__":
    conn = get_connection()
    engine = RecommendationEngine()
    recs = engine.generate_for_all_high_risk(conn, threshold=80.0)
    print(recs)
    conn.close()
