import sys
import logging
from collections import Counter
import config
from warehouse.db_connection import get_connection
from genai.recommendation_engine import RecommendationEngine
from genai.insights_engine import InsightsEngine

logger = logging.getLogger("clara.genai.run_recommendations")

def main():
    """
    Orchestration script that runs the GenAI recommendation pipeline.
    Works seamlessly in both Live Gemini Mode and Offline Fallback Mode.
    Queries high-risk instances, generates recommendations, stores them idempotently,
    and displays executive summary metrics.
    """
    conn = get_connection()
    threshold = getattr(config, "RECOMMENDATION_THRESHOLD", 50.0)
    limit = getattr(config, "TOP_N_RECOMMENDATIONS", 10)

    try:
        print("\n=== CLARA Remediation & Recommendation Orchestrator ===")
        # 1. Instantiate Recommendation Engine
        engine = RecommendationEngine()
        mode_str = "Live Gemini" if engine.client.is_configured else "Deterministic Offline Fallback"
        print(f"GenAI [Orchestrator]: Active Generation Mode: {mode_str}")

        # 2. Generate recommendations for top high-risk instances
        recs = engine.generate_for_all_high_risk(conn, threshold=threshold, limit=limit)

        if not recs:
            print(f"GenAI [Orchestrator]: No high-risk instances found exceeding threshold {threshold}.")
            return []

        # 3. Save recommendations into database
        engine.save_recommendations(conn, recs)

        # 4. Generate executive summary text report
        insights = InsightsEngine()
        summary = insights.generate_executive_summary(conn)

        # 5. Print summary report and priorities count breakdown
        print("\n=== EXECUTIVE SUMMARY REPORT ===")
        print(summary)
        print("\n=== RECOMMENDATION BREAKDOWN ===")

        priorities = [rec.get("priority", "Medium") for rec in recs]
        p_counts = Counter(priorities)
        for priority, count in p_counts.items():
            print(f"- Priority {priority:<10} : {count} recommendation(s)")

        sources = [rec.get("generation_source", "unknown") for rec in recs]
        s_counts = Counter(sources)
        for src, count in s_counts.items():
            print(f"- Source {src:<12} : {count} recommendation(s)")

        return recs

    except Exception as e:
        logger.error(f"GenAI [Orchestrator]: Recommendation generation encountered an error: {e}", exc_info=False)
        print(f"GenAI [Orchestrator]: Recovered gracefully from error: {e}")
        return []
    finally:
        conn.close()

if __name__ == "__main__":
    main()
