from genai.gemini_client import GeminiClient
from warehouse.db_connection import get_connection

class InsightsEngine:
    """
    NLG Insights engine compiling database summary statistics and generating
    high-level business narratives for decision makers.
    """
    def __init__(self):
        self.client = GeminiClient()

    def generate_executive_summary(self, conn) -> str:
        """
        Compiles database metrics aggregates and prompts Gemini to write a 3-sentence
        executive overview summary.

        Parameters:
            conn (duckdb.DuckDBPyConnection): Active DuckDB connection.

        Returns:
            str: Generated summary text.
        """
        print("GenAI [Insights]: Fetching database aggregate metrics for executive report...")
        
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
        
        # Build priority breakdown description
        priority_str = ", ".join([f"{p}: {count}" for p, count in priorities.items()]) if priorities else "none"

        sys_prompt = "You are an executive assistant summarizing cloud infrastructure health metrics."
        
        user_prompt = f"""
        Write a 3-sentence executive summary in plain business English describing the state of our cloud environment based on these statistics:
        - Total instances monitored: {total_inst}
        - Critical overall risk instances (risk score > 70): {critical_count}
        - Total potential monthly savings opportunity: ${total_savings:,.2f}
        - Recommendations count by priority: {priority_str}
        
        Guidelines:
        - Focus on impact, cost savings, and security.
        - Return ONLY the 3-sentence summary, no extra sentences or headings.
        """
        
        summary = self.client.generate_text(sys_prompt, user_prompt)
        return summary

if __name__ == "__main__":
    conn = get_connection()
    engine = InsightsEngine()
    summary = engine.generate_executive_summary(conn)
    print(summary)
    conn.close()
