import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from warehouse.db_connection import get_connection

class AnomalyDetector:
    """
    Isolation Forest anomaly detector that flags instances displaying anomalous
    telemetry patterns in CPU, memory, and network utilisation.
    """
    def __init__(self):
        self.model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
        self.feature_columns = None
        self.cached_features = None

    def _build_features(self, conn) -> pd.DataFrame:
        """
        Queries daily metrics, groups by instance_id, and computes per-instance metrics features.
        
        Parameters:
            conn (duckdb.DuckDBPyConnection): Active DuckDB connection.
            
        Returns:
            pd.DataFrame: Features DataFrame indexed by instance_id.
        """
        if self.cached_features is not None:
            return self.cached_features

        # Push the GROUP BY and aggregations to DuckDB for high performance
        query = """
            SELECT 
                instance_id,
                AVG(cpu_utilization_pct) AS cpu_mean,
                STDDEV(cpu_utilization_pct) AS cpu_std,
                MAX(cpu_utilization_pct) AS cpu_max,
                AVG(memory_utilization_pct) AS memory_mean,
                STDDEV(memory_utilization_pct) AS memory_std,
                MAX(memory_utilization_pct) AS memory_max,
                MAX(network_out_mb) AS network_out_max,
                STDDEV(network_out_mb) AS network_out_std
            FROM metrics_daily
            GROUP BY instance_id
        """
        features_df = conn.execute(query).fetchdf()
        features_df = features_df.set_index("instance_id")
        
        # Fill standard deviations with 0 if NaN (e.g. for single-row cases)
        features_df["cpu_std"] = features_df["cpu_std"].fillna(0.0)
        features_df["memory_std"] = features_df["memory_std"].fillna(0.0)
        features_df["network_out_std"] = features_df["network_out_std"].fillna(0.0)
        
        self.cached_features = features_df
        return features_df

    def train(self, conn):
        """
        Generates per-instance metrics features and fits the IsolationForest model.

        Parameters:
            conn (duckdb.DuckDBPyConnection): Active DuckDB connection.
        """
        print("Analytics [Anomaly]: Building training features...")
        features = self._build_features(conn)
        self.feature_columns = list(features.columns)
        
        print("Analytics [Anomaly]: Training Isolation Forest model...")
        self.model.fit(features[self.feature_columns])
        return self

    def predict(self, conn) -> pd.DataFrame:
        """
        Scores instance telemetry profiles. Maps decision_function outputs to a 0-100 anomaly_score.

        Parameters:
            conn (duckdb.DuckDBPyConnection): Active DuckDB connection.

        Returns:
            pd.DataFrame: Columns [instance_id, anomaly_score].
        """
        if self.feature_columns is None:
            raise RuntimeError("Model must be trained or loaded before making predictions.")
            
        features = self._build_features(conn)
        X = features[self.feature_columns]
        
        # decision_function: lower values are more anomalous
        decision = self.model.decision_function(X)
        
        # Normalise decision scores to 0-100 range where lower decision maps to higher anomaly_score
        min_d = decision.min()
        max_d = decision.max()
        
        if max_d - min_d > 1e-5:
            norm_d = (decision - min_d) / (max_d - min_d)
        else:
            norm_d = np.zeros_like(decision)
            
        anomaly_score = 100 * (1 - norm_d)
        
        output_df = pd.DataFrame({
            "instance_id": features.index,
            "anomaly_score": np.round(anomaly_score, 4)
        })
        return output_df

    def save(self, path=None):
        """
        Saves the fitted model using joblib.
        """
        if path is None:
            path = os.path.abspath(os.path.join(os.path.dirname(__file__), "saved_models", "anomaly_model.pkl"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            "model": self.model,
            "feature_columns": self.feature_columns
        }, path)
        print(f"Analytics [Anomaly]: Model saved to {path}")

    def load(self, path=None):
        """
        Loads the model from file using joblib.
        """
        if path is None:
            path = os.path.abspath(os.path.join(os.path.dirname(__file__), "saved_models", "anomaly_model.pkl"))
        if not os.path.exists(path):
            raise FileNotFoundError(f"Saved model file not found at {path}")
            
        data = joblib.load(path)
        self.model = data["model"]
        self.feature_columns = data["feature_columns"]
        print(f"Analytics [Anomaly]: Model loaded from {path}")
        return self

if __name__ == "__main__":
    conn = get_connection()
    detector = AnomalyDetector()
    detector.train(conn)
    preds = detector.predict(conn)
    print(preds.head())
    conn.close()
