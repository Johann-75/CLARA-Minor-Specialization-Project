import sys
from collections import Counter
import config
from warehouse.db_connection import get_connection
from genai.recommendation_engine import RecommendationEngine
from genai.insights_engine import InsightsEngine

def main():
    """
    Orchestration script that runs the GenAI recommendation pipeline.
    Queries risk scores, generates recommendations for high-risk instances,
    saves recommendations, and prints an executive summary report.
    """
    # 1. Establish database connection
    conn = get_connection()
    
    threshold = config.RECOMMENDATION_THRESHOLD
    
    try:
        # 2. Instantiate Recommendation Engine
        engine = RecommendationEngine()
        
        # 3. Generate recommendations for all high-risk instances
        recs = engine.generate_for_all_high_risk(conn, threshold=threshold)
        
        # Handle the case where zero instances exceed the threshold gracefully
        if not recs:
            print(f"No high-risk instances found above threshold {threshold}")
            return
            
        # 4. Save recommendations into database
        engine.save_recommendations(conn, recs)
        
        # 5. Generate executive summary text report
        insights = InsightsEngine()
        summary = insights.generate_executive_summary(conn)
        
        # 6. Print summary report and priorities count breakdown
        print("\n=== EXECUTIVE SUMMARY REPORT ===")
        print(summary)
        print("\n=== RECOMMENDATION COUNTS BY PRIORITY ===")
        
        priorities = [rec.get("priority", "Medium") for rec in recs]
        counts = Counter(priorities)
        for priority, count in counts.items():
            print(f"- {priority:<10} : {count} recommendation(s)")
            
    except Exception as e:
        print(f"GenAI [Orchestration]: Pipeline failed with error: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
