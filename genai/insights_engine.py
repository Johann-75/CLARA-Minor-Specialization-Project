import logging
from typing import Optional
from genai.gemini_client import GeminiClient
from warehouse.db_connection import get_connection, migrate_schema

logger = logging.getLogger("clara.genai.insights_engine")

class InsightsEngine:
    """
    NLG Insights engine compiling database summary statistics and generating
    high-level business narratives for decision makers.
    Supports live Gemini narrative generation with deterministic fallback.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.client = GeminiClient(api_key=api_key)

    def generate_executive_summary(self, conn) -> str:
        """
        Compiles database metrics aggregates and generates an executive overview summary.
        Uses gemini-3.8-flash if configured, or a deterministic fallback summary if offline.
        """
        migrate_schema(conn)

        logger.info("GenAI [Insights]: Fetching database aggregate metrics for executive report...")
        
        # 1. Total instance counts
        total_inst = conn.execute("SELECT COUNT(*) FROM cloud_instances").fetchone()[0]
        
        # 2. Critical score counts
        critical_count = conn.execute("SELECT COUNT(*) FROM risk_scores WHERE overall_risk_score > 70").fetchone()[0]
        
        # 3. Aggregated financial savings opportunity
        savings_val = conn.execute("SELECT SUM(estimated_savings_usd) FROM recommendations").fetchone()[0]
        total_savings = float(savings_val) if savings_val is not None else 0.0
        
        # 4. Recommendation Priority breakdowns
        priority_rows = conn.execute("SELECT priority, COUNT(*) FROM recommendations GROUP BY priority").fetchall()
        priorities = {row[0]: row[1] for row in priority_rows}
        priority_str = ", ".join([f"{p}: {count}" for p, count in priorities.items()]) if priorities else "none"

        # Check generation sources
        source_rows = conn.execute("SELECT generation_source, COUNT(*) FROM recommendations GROUP BY generation_source").fetchall()
        sources_summary = ", ".join([f"{s[0]}: {s[1]}" for s in source_rows]) if source_rows else "none"

        # Fallback text generator
        deterministic_summary = (
            f"[Deterministic Fallback Summary] Environment monitoring encompasses {total_inst} cloud instances across multiple providers. "
            f"Currently, {critical_count} instances exhibit elevated risk (>70) requiring active remediation. "
            f"Identified remediation opportunities offer an estimated potential monthly cost optimization of ${total_savings:,.2f} "
            f"across {priority_str} priority work items."
        )

        if not self.client.is_configured:
            logger.info("GenAI [Insights]: GEMINI_API_KEY unconfigured; generating deterministic executive summary.")
            return deterministic_summary

        sys_prompt = "You are an executive assistant summarizing cloud infrastructure health metrics."
        user_prompt = f"""
        Write a concise 3-sentence executive summary in plain business English describing the state of our cloud environment based on these statistics:
        - Total instances monitored: {total_inst}
        - Critical overall risk instances (risk score > 70): {critical_count}
        - Total potential monthly savings opportunity: ${total_savings:,.2f}
        - Recommendations count by priority: {priority_str}
        - Recommendation sources: {sources_summary}
        
        Guidelines:
        - Focus on impact, cost savings, and security posture.
        - Return ONLY the 3-sentence summary, no extra headings.
        """

        summary_text, err = self.client.generate_text(sys_prompt, user_prompt)
        if summary_text and not err:
            return summary_text.strip()

        logger.warning(f"GenAI [Insights]: Gemini narrative generation failed ({err}). Using deterministic summary.")
        return deterministic_summary

if __name__ == "__main__":
    conn = get_connection()
    engine = InsightsEngine()
    summary = engine.generate_executive_summary(conn)
    print(summary)
    conn.close()
