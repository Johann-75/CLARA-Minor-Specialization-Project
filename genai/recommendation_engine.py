import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
import config
from warehouse.db_connection import get_connection, migrate_schema
from genai.gemini_client import GeminiClient
from genai.schemas import (
    GeminiRecommendationBatchResponse,
    GeminiRecommendationItem,
)

logger = logging.getLogger("clara.genai.recommendation_engine")

class RecommendationEngine:
    """
    Production-ready recommendation engine supporting:
    1. Live Gemini structured generation with gemini-3.8-flash
    2. Deterministic offline fallback rule engine (explicitly labeled)
    3. Graceful Gemini error fallback with safe error categorization
    4. Anti-hallucination validation and idempotent storage
    """
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.client = GeminiClient(api_key=api_key, model_name=model_name)
        self.default_model_name = self.client.model_name or "gemini-3.8-flash"

    def _determine_risk_type(self, row: dict) -> str:
        """
        Determines the primary/dominant risk type based on risk sub-scores.
        """
        sec = float(row.get("security_risk_score", 0.0))
        anom = float(row.get("anomaly_score", 0.0))
        cost = float(row.get("cost_waste_score", 0.0))

        if sec >= anom and sec >= cost:
            return "security"
        elif anom >= cost:
            return "anomaly"
        else:
            return "cost"

    def _determine_priority(self, overall_risk_score: float) -> str:
        """
        Calibrates remediation priority from the overall risk score.
        """
        if overall_risk_score >= 80.0:
            return "Critical"
        elif overall_risk_score >= 60.0:
            return "High"
        elif overall_risk_score >= 40.0:
            return "Medium"
        else:
            return "Low"

    def generate_offline_recommendation(
        self,
        instance_row: dict,
        risk_type: Optional[str] = None,
        fallback_reason: str = "missing_api_key"
    ) -> dict:
        """
        Deterministic rule-based fallback recommendation engine.
        Produces high-quality, grounded recommendations citing observable metrics
        and explicitly tags them as offline fallback content.
        """
        if risk_type is None:
            risk_type = self._determine_risk_type(instance_row)

        inst_id = str(instance_row.get("instance_id", "unknown"))
        sec = float(instance_row.get("security_risk_score", 0.0))
        anom = float(instance_row.get("anomaly_score", 0.0))
        cost_waste = float(instance_row.get("cost_waste_score", 0.0))
        overall = float(instance_row.get("overall_risk_score", max(sec, anom, cost_waste)))
        priority = self._determine_priority(overall)

        ports = str(instance_row.get("open_ports", ""))
        internet_exposed = bool(instance_row.get("internet_exposed", False))
        encryption_enabled = bool(instance_row.get("encryption_enabled", True))
        iam_level = str(instance_row.get("iam_permission_level", "standard"))
        failed_logins = int(instance_row.get("failed_logins_7d", 0))
        daily_cost = float(instance_row.get("daily_cost_usd", 0.0))
        monthly_cost = daily_cost * 30.0
        util_pct = float(instance_row.get("utilization_pct", 0.0))

        estimated_savings = 0.0
        effort_hours = 1.0

        if risk_type == "security":
            has_remote_ports = any(p in ports for p in ["22", "3389", "21", "23"])
            if internet_exposed and has_remote_ports:
                title = "Restrict public administrative ingress ports"
                desc = (
                    f"Instance {inst_id} exposes remote management ports ({ports}) directly to the public internet, "
                    f"yielding a security risk score of {sec:.1f}/100. This configuration represents an active perimeter exposure."
                )
                steps = [
                    f"Update security group to revoke 0.0.0.0/0 ingress on ports {ports}",
                    "Route administrative traffic through a hardened corporate bastion or client VPN",
                    "Enable automated security group drift detection and alerting"
                ]
                effort_hours = 1.0
            elif failed_logins > 10:
                title = "Mitigate repeated authentication brute-force activity"
                desc = (
                    f"Instance {inst_id} recorded {failed_logins} failed login attempts over 7 days with security risk {sec:.1f}/100, "
                    f"indicating sustained brute-force credential stuffing."
                )
                steps = [
                    "Rotate all administrative SSH keys and service credentials",
                    "Deploy fail2ban or equivalent IP rate-limiting rules on host authentication daemons",
                    "Review authentication logs for unauthorized access and enforce MFA"
                ]
                effort_hours = 2.0
            elif not encryption_enabled:
                title = "Remediate unencrypted storage volume baseline"
                desc = (
                    f"Instance {inst_id} storage volume is unencrypted, conflicting with standard cloud compliance baselines "
                    f"under security risk score {sec:.1f}/100."
                )
                steps = [
                    "Create point-in-time snapshot of the target unencrypted volume",
                    "Copy snapshot with customer-managed KMS encryption enabled",
                    "Swap instance volume attachment during scheduled maintenance window"
                ]
                effort_hours = 2.5
            elif iam_level == "excessive":
                title = "Enforce least-privilege IAM instance role"
                desc = (
                    f"Instance {inst_id} is assigned an excessive IAM profile with wildcard administrative permissions, "
                    f"elevating blast radius risk ({sec:.1f}/100)."
                )
                steps = [
                    "Audit past 30 days of instance IAM API actions via CloudTrail/Activity Log",
                    "Formulate scoped policy containing only observed necessary API actions",
                    "Replace existing broad policy attachment with least-privilege role"
                ]
                effort_hours = 1.5
            else:
                title = "Review cloud security configuration posture"
                desc = (
                    f"Instance {inst_id} exhibits elevated security risk score ({sec:.1f}/100) across multiple configuration parameters."
                )
                steps = [
                    "Perform comprehensive CIS benchmark scan on the instance",
                    "Apply missing OS security patches and update baseline packages",
                    "Verify security group ingress boundaries"
                ]
                effort_hours = 1.0

        elif risk_type == "cost":
            title = "Rightsize underutilized cloud compute instance"
            if cost_waste >= 70.0:
                estimated_savings = float(monthly_cost * 0.90)
            else:
                estimated_savings = float(monthly_cost * 0.50)
            desc = (
                f"Instance {inst_id} has average utilization of {util_pct:.1f}% with monthly cost of ${monthly_cost:.2f}, "
                f"resulting in a high cost waste score of {cost_waste:.1f}/100."
            )
            steps = [
                "Inspect historical CPU and memory peak headroom over the last 14 days",
                "Schedule maintenance window to resize instance to next smaller family tier",
                "Verify application operational latency post-downsize"
            ]
            effort_hours = 1.0

        else: # anomaly
            title = "Investigate anomalous telemetry pattern deviation"
            desc = (
                f"Isolation Forest identified significant behavioral anomaly on {inst_id} (anomaly score {anom:.1f}/100), "
                f"diverging significantly from cohort peer baselines."
            )
            steps = [
                "Examine process monitoring metrics for unexpected spikes in CPU, memory, or network I/O",
                "Cross-reference recent application deployment or cron scheduler logs",
                "Establish temporary threshold alarms to track recurrence"
            ]
            effort_hours = 1.5

        return {
            "instance_id": inst_id,
            "risk_type": risk_type,
            "priority": priority,
            "title": title,
            "description": desc,
            "implementation_steps": steps,
            "estimated_savings_usd": round(estimated_savings, 2),
            "estimated_effort_hours": effort_hours,
            "generation_source": "offline_fallback",
            "model_name": "deterministic_rule_engine",
            "fallback_reason": fallback_reason,
            "expected_benefit": f"Reduction in {risk_type} risk and enhanced operational stability."
        }

    def generate_recommendation(self, instance_row: dict, risk_type: Optional[str] = None) -> dict:
        """
        Generates a recommendation for a single instance row.
        Attempts live Gemini if configured, otherwise falls back gracefully to offline engine.
        """
        if risk_type is None:
            risk_type = self._determine_risk_type(instance_row)

        if self.client.is_configured:
            sys_prompt, user_prompt = self._build_batch_prompts([instance_row])
            parsed_batch, error_category = self.client.generate_structured(
                system_prompt=sys_prompt,
                user_prompt=user_prompt,
                response_schema=GeminiRecommendationBatchResponse
            )
            if parsed_batch and parsed_batch.recommendations:
                item = parsed_batch.recommendations[0]
                # Anti-hallucination check
                target_id = instance_row.get("instance_id")
                if item.instance_id == target_id:
                    steps = item.recommended_action
                    if isinstance(steps, str):
                        step_list = [s.strip() for s in steps.splitlines() if s.strip()] or [steps]
                    elif isinstance(steps, list):
                        step_list = steps
                    else:
                        step_list = [str(steps)]

                    savings = float(item.estimated_savings_usd)
                    if savings <= 0.0 and instance_row.get("cost_waste_score", 0.0) >= 70.0:
                        savings = float(instance_row.get("daily_cost_usd", 0.0) * 30.0 * 0.9)

                    return {
                        "instance_id": target_id,
                        "risk_type": risk_type,
                        "priority": item.priority,
                        "title": item.title,
                        "description": item.explanation,
                        "implementation_steps": step_list,
                        "estimated_savings_usd": round(savings, 2),
                        "estimated_effort_hours": float(item.estimated_effort_hours or 1.0),
                        "generation_source": "gemini",
                        "model_name": self.default_model_name,
                        "fallback_reason": None,
                        "expected_benefit": item.expected_benefit
                    }

            # If Gemini call failed or returned empty/mismatched item
            safe_reason = error_category or "schema_validation_error"
            return self.generate_offline_recommendation(instance_row, risk_type=risk_type, fallback_reason=safe_reason)

        return self.generate_offline_recommendation(instance_row, risk_type=risk_type, fallback_reason="missing_api_key")

    def _build_batch_prompts(self, rows: List[dict]) -> tuple[str, str]:
        """
        Builds system and user prompts for batch structured recommendation generation.
        """
        system_prompt = (
            "You are a Principal Cloud Security and FinOps Architect. "
            "Analyze the provided cloud instances telemetry, security posture, and cost data. "
            "For each provided instance, generate ONE specific, actionable recommendation.\n\n"
            "STRICT CONSTRAINTS:\n"
            "1. You must ONLY output recommendations for the exact instance IDs provided in the user prompt.\n"
            "2. Never hallucinate, invent, or output instance IDs that were not explicitly listed.\n"
            "3. Ground all explanations strictly in the numeric risk scores, ports, failed logins, or costs provided.\n"
            "4. Priority must be strictly one of: 'Critical', 'High', 'Medium', 'Low'.\n"
            "5. Source must be 'gemini' and model_name must be 'gemini-3.8-flash'."
        )

        lines = ["Here are the target cloud instances requiring prioritized remediation:"]
        for row in rows:
            inst_id = row.get("instance_id")
            sec = float(row.get("security_risk_score", 0.0))
            anom = float(row.get("anomaly_score", 0.0))
            cost = float(row.get("cost_waste_score", 0.0))
            overall = float(row.get("overall_risk_score", 0.0))
            provider = row.get("cloud_provider", "Cloud")
            region = row.get("region", "global")
            itype = row.get("instance_type", "compute")
            ports = str(row.get("open_ports", "none"))
            exposed = bool(row.get("internet_exposed", False))
            enc = bool(row.get("encryption_enabled", True))
            iam = str(row.get("iam_permission_level", "standard"))
            failed_logins = int(row.get("failed_logins_7d", 0))
            daily_cost = float(row.get("daily_cost_usd", 0.0))
            monthly = daily_cost * 30.0
            util = float(row.get("utilization_pct", 0.0))

            lines.append(
                f"- Instance ID: {inst_id} | Provider: {provider} ({region}) | Type: {itype}\n"
                f"  Scores: Overall={overall:.1f}, Security={sec:.1f}, Anomaly={anom:.1f}, CostWaste={cost:.1f}\n"
                f"  Posture: OpenPorts=[{ports}], InternetExposed={exposed}, Encrypted={enc}, IAM={iam}, FailedLogins7d={failed_logins}\n"
                f"  Cost/Perf: MonthlySpend=${monthly:.2f}, AvgCpu={util:.1f}%\n"
            )

        lines.append("Generate prioritized recommendations conforming strictly to the requested schema.")
        return system_prompt, "\n".join(lines)

    def generate_for_all_high_risk(
        self,
        conn,
        threshold: Optional[float] = None,
        limit: Optional[int] = None
    ) -> List[dict]:
        """
        Retrieves high-risk instances and generates recommendations using:
        - Live Gemini API if key is present and call succeeds
        - Graceful offline deterministic fallback if key is missing, invalid, or API call fails
        
        Strictly validates that returned recommendations match queried instance IDs.
        """
        migrate_schema(conn)

        if threshold is None:
            threshold = getattr(config, "RECOMMENDATION_THRESHOLD", 50.0)
        if limit is None:
            limit = getattr(config, "TOP_N_RECOMMENDATIONS", 10)

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
              AND rs.overall_risk_score >= ?
            ORDER BY rs.overall_risk_score DESC
            LIMIT ?
        """

        df = conn.execute(query, (threshold, limit)).fetchdf()
        if df.empty:
            logger.info(f"No instances found exceeding overall risk threshold {threshold}")
            return []

        rows = df.to_dict(orient="records")
        target_ids = {r["instance_id"]: r for r in rows}
        recommendations: List[dict] = []

        # Operational Mode 1 & 3: Attempt Live Gemini if configured
        if self.client.is_configured:
            logger.info(f"GenAI: Generating live Gemini recommendations for {len(rows)} instances using {self.client.model_name}...")
            sys_prompt, user_prompt = self._build_batch_prompts(rows)
            parsed_batch, error_category = self.client.generate_structured(
                system_prompt=sys_prompt,
                user_prompt=user_prompt,
                response_schema=GeminiRecommendationBatchResponse
            )

            if parsed_batch is not None and parsed_batch.recommendations:
                # Anti-hallucination validation: verify instance IDs belong to target_ids
                valid_gemini_recs = {}
                for item in parsed_batch.recommendations:
                    if item.instance_id in target_ids and item.instance_id not in valid_gemini_recs:
                        valid_gemini_recs[item.instance_id] = item
                    else:
                        logger.warning(f"GenAI [Guard]: Rejected unknown or duplicate hallucinated instance ID: {item.instance_id}")

                for inst_id, row in target_ids.items():
                    if inst_id in valid_gemini_recs:
                        g_rec = valid_gemini_recs[inst_id]
                        risk_type = self._determine_risk_type(row)
                        steps = g_rec.recommended_action
                        if isinstance(steps, str):
                            step_list = [s.strip() for s in steps.splitlines() if s.strip()] or [steps]
                        elif isinstance(steps, list):
                            step_list = steps
                        else:
                            step_list = [str(steps)]

                        savings = float(g_rec.estimated_savings_usd)
                        if savings <= 0.0 and row.get("cost_waste_score", 0.0) >= 70.0:
                            savings = float(row.get("daily_cost_usd", 0.0) * 30.0 * 0.9)

                        recommendations.append({
                            "instance_id": inst_id,
                            "risk_type": risk_type,
                            "priority": g_rec.priority,
                            "title": g_rec.title,
                            "description": g_rec.explanation,
                            "implementation_steps": step_list,
                            "estimated_savings_usd": round(savings, 2),
                            "estimated_effort_hours": float(g_rec.estimated_effort_hours or 1.0),
                            "generation_source": "gemini",
                            "model_name": self.default_model_name,
                            "fallback_reason": None,
                            "expected_benefit": g_rec.expected_benefit
                        })
                    else:
                        # Item missed in batch response -> deterministic fallback
                        logger.info(f"GenAI: Target {inst_id} absent in Gemini batch, applying deterministic fallback.")
                        rec = self.generate_offline_recommendation(row, fallback_reason="schema_validation_error")
                        recommendations.append(rec)

                logger.info(f"GenAI: Successfully produced {len(recommendations)} recommendations (live Gemini).")
                return recommendations
            else:
                # Gemini Error Fallback
                safe_reason = error_category or "api_error"
                logger.warning(f"GenAI: Gemini API failed ({safe_reason}). Activating graceful deterministic fallback.")
                for row in rows:
                    rec = self.generate_offline_recommendation(row, fallback_reason=safe_reason)
                    recommendations.append(rec)
                return recommendations

        # Operational Mode 2: Deterministic Offline Fallback Mode
        logger.info("GenAI: GEMINI_API_KEY unconfigured. Generating offline deterministic fallback recommendations.")
        for row in rows:
            rec = self.generate_offline_recommendation(row, fallback_reason="missing_api_key")
            recommendations.append(rec)

        return recommendations

    def save_recommendations(self, conn, recommendations: List[dict]):
        """
        Persists recommendations into the DuckDB recommendations table idempotently.
        Ensures schema migrations are applied and avoids duplicate records.
        """
        migrate_schema(conn)

        print("GenAI [Recommendations]: Refreshing recommendation records...")
        conn.execute("DELETE FROM recommendations")

        if not recommendations:
            print("GenAI [Recommendations]: Zero recommendations to insert.")
            return

        print(f"GenAI [Recommendations]: Storing {len(recommendations)} recommendations...")

        insert_query = """
            INSERT INTO recommendations (
                recommendation_id, instance_id, risk_type, priority, title,
                description, implementation_steps, estimated_savings_usd,
                estimated_effort_hours, status, generated_at,
                generation_source, model_name, fallback_reason, expected_benefit
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                datetime.now(),
                rec.get("generation_source", "offline_fallback"),
                rec.get("model_name", "deterministic_rule_engine"),
                rec.get("fallback_reason"),
                rec.get("expected_benefit")
            ))

        print("GenAI [Recommendations]: Storage complete.")
