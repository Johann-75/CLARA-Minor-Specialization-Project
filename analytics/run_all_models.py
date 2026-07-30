import uuid
import pandas as pd
from datetime import datetime
import config
from warehouse.db_connection import get_connection
from analytics.anomaly_model import AnomalyDetector
from analytics.security_model import SecurityRiskModel
from analytics.cost_model import CostWasteModel

def main():
    """
    Orchestrates the training and execution of the three CLARA models.
    Computes overall risk scores and updates the database warehouse.
    """
    # 1. Connect to DuckDB warehouse
    conn = get_connection()
    
    try:
        # 2. Run Anomaly Detector (train & predict)
        anomaly_model = AnomalyDetector()
        anomaly_model.train(conn)
        df_anomaly = anomaly_model.predict(conn)
        
        # Save model for persistence
        anomaly_model.save()
        
        # 3. Run Security Risk Model (heuristic scoring)
        security_model = SecurityRiskModel()
        df_security = security_model.calculate_risk(conn)
        
        # 4. Run Cost Waste Model (train & predict)
        cost_model = CostWasteModel()
        cost_model.train(conn)
        df_cost = cost_model.predict(conn)
        
        # Save model for persistence
        cost_model.save()
        
        # 5. Merge all model predictions on instance_id
        print("Analytics: Merging model risk scoring outputs...")
        merged_df = pd.merge(df_security, df_anomaly, on="instance_id")
        merged_df = pd.merge(merged_df, df_cost, on="instance_id")
        
        # 6. Compute overall risk score using weighted average
        # (Security: 50%, Anomaly: 30%, Cost Waste: 20%)
        merged_df["overall_risk_score"] = (
            merged_df["security_risk_score"] * 0.5 +
            merged_df["anomaly_score"] * 0.3 +
            merged_df["cost_waste_score"] * 0.2
        )
        merged_df["overall_risk_score"] = merged_df["overall_risk_score"].round(4)
        
        # 7. Write to risk_scores table
        print("Analytics: Writing risk scores to DuckDB database...")
        
        # Generate metadata columns
        merged_df["score_id"] = [str(uuid.uuid4()) for _ in range(len(merged_df))]
        merged_df["model_version"] = config.MODEL_VERSION
        merged_df["calculated_at"] = datetime.now()
        
        # Select exact schema columns
        db_columns = [
            "score_id",
            "instance_id",
            "anomaly_score",
            "security_risk_score",
            "cost_waste_score",
            "overall_risk_score",
            "model_version",
            "calculated_at"
        ]
        df_to_insert = merged_df[db_columns]
        
        # Safely truncate existing risk_scores records
        conn.execute("DELETE FROM risk_scores")
        
        # Bulk load using DuckDB pandas registration
        conn.register("temp_risk_scores", df_to_insert)
        conn.execute("INSERT INTO risk_scores SELECT * FROM temp_risk_scores")
        conn.unregister("temp_risk_scores")
        print(f"Analytics: Successfully loaded {len(df_to_insert)} risk score records into the warehouse.")
        
        # 8. Print Top 10 Summary table
        print("\n=== TOP 10 RISK INSTANCES ===")
        top_10 = merged_df.sort_values(by="overall_risk_score", ascending=False).head(10)
        
        print(top_10[[
            "instance_id", 
            "security_risk_score", 
            "anomaly_score", 
            "cost_waste_score", 
            "overall_risk_score"
        ]].to_string(index=False))

    except Exception as e:
        print(f"Analytics: Pipeline orchestration failed with error: {e}")
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    main()
