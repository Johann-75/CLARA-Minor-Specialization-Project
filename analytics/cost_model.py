import os
import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from warehouse.db_connection import get_connection

class CostWasteModel:
    """
    Cost waste prediction model using K-Means clustering to discover underutilised nodes
    and mapping their metrics to projected monthly savings.
    """
    def __init__(self):
        self.model = KMeans(n_clusters=3, random_state=42, n_init=10)
        self.waste_cluster_id = None
        self.feature_columns = ["avg_utilization_pct", "avg_daily_cost_usd"]
        self.cached_features = None

    def _build_features(self, conn) -> pd.DataFrame:
        """
        Queries cost_data and metrics_daily tables and aggregates features per instance.

        Parameters:
            conn (duckdb.DuckDBPyConnection): Active DuckDB connection.

        Returns:
            pd.DataFrame: Features DataFrame indexed by instance_id.
        """
        if self.cached_features is not None:
            return self.cached_features

        query = """
            SELECT 
                m.instance_id, 
                AVG(m.cpu_utilization_pct) AS avg_utilization_pct,
                AVG(c.daily_cost_usd) AS avg_daily_cost_usd,
                AVG(c.waste_score) AS avg_waste_score
            FROM metrics_daily m
            JOIN cost_data c ON m.instance_id = c.instance_id AND m.date = c.date
            GROUP BY m.instance_id
        """
        df = conn.execute(query).fetchdf()
        self.cached_features = df.set_index("instance_id")
        return self.cached_features

    def train(self, conn):
        """
        Fits KMeans cluster model on utilization and daily cost, identifying the waste cluster.

        Parameters:
            conn (duckdb.DuckDBPyConnection): Active DuckDB connection.
        """
        print("Analytics [Cost]: Aggregating cost and utilization metrics...")
        features = self._build_features(conn)
        X = features[self.feature_columns]
        
        print("Analytics [Cost]: Clustering instances via KMeans...")
        self.model.fit(X)
        
        # Identify the waste cluster as the one with the lowest mean CPU utilization
        features["cluster_id"] = self.model.labels_
        cluster_means = features.groupby("cluster_id")["avg_utilization_pct"].mean()
        self.waste_cluster_id = int(cluster_means.idxmin())
        
        print(f"Analytics [Cost]: Underutilized cluster identified as ID {self.waste_cluster_id} "
              f"(Mean CPU: {cluster_means[self.waste_cluster_id]:.2f}%)")
        return self

    def predict(self, conn) -> pd.DataFrame:
        """
        Calculates predicted waste score (0-100) and estimated monthly savings.

        Parameters:
            conn (duckdb.DuckDBPyConnection): Active DuckDB connection.

        Returns:
            pd.DataFrame: Columns [instance_id, cost_waste_score, estimated_monthly_savings_usd].
        """
        if self.waste_cluster_id is None:
            raise RuntimeError("Model must be trained or loaded before making predictions.")
            
        features = self._build_features(conn)
        X = features[self.feature_columns]
        
        # Assign cluster labels
        labels = self.model.predict(X)
        features["cluster_id"] = labels
        
        # Calculate predicted waste score:
        # - Waste cluster: scale 70-100 based on low CPU utilization
        # - Other clusters: scale 0-40 based on low CPU utilization
        waste_mask = features["cluster_id"] == self.waste_cluster_id
        
        cpu_waste = features.loc[waste_mask, "avg_utilization_pct"]
        cpu_non_waste = features.loc[~waste_mask, "avg_utilization_pct"]
        
        waste_scores = pd.Series(index=features.index, dtype=float)
        
        # Scale waste scores for underutilized cluster (lower utilization = higher waste score)
        if not cpu_waste.empty:
            min_w = cpu_waste.min()
            max_w = cpu_waste.max()
            if max_w - min_w > 1e-5:
                # Normalize to 0-1, invert, scale to 70-100
                norm = (cpu_waste - min_w) / (max_w - min_w)
                waste_scores.loc[waste_mask] = 70.0 + 30.0 * (1.0 - norm)
            else:
                waste_scores.loc[waste_mask] = 85.0
        
        # Scale waste scores for other clusters (lower utilization = higher waste score, but capped at 40)
        if not cpu_non_waste.empty:
            min_nw = cpu_non_waste.min()
            max_nw = cpu_non_waste.max()
            if max_nw - min_nw > 1e-5:
                norm = (cpu_non_waste - min_nw) / (max_nw - min_nw)
                waste_scores.loc[~waste_mask] = 40.0 * (1.0 - norm)
            else:
                waste_scores.loc[~waste_mask] = 20.0
                
        # Calculate estimated monthly savings (90% recovery rate, only for waste cluster)
        savings = np.where(
            labels == self.waste_cluster_id,
            features["avg_daily_cost_usd"] * 30 * 0.9,
            0.0
        )
        
        output_df = pd.DataFrame({
            "instance_id": features.index,
            "cost_waste_score": np.round(waste_scores.values, 4),
            "estimated_monthly_savings_usd": np.round(savings, 4)
        })
        return output_df

    def save(self, path=None):
        """
        Saves the fitted model and cluster mapping using joblib.
        """
        if path is None:
            path = os.path.abspath(os.path.join(os.path.dirname(__file__), "saved_models", "cost_model.pkl"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            "model": self.model,
            "waste_cluster_id": self.waste_cluster_id,
            "feature_columns": self.feature_columns
        }, path)
        print(f"Analytics [Cost]: Model saved to {path}")

    def load(self, path=None):
        """
        Loads the model and cluster parameters from joblib.
        """
        if path is None:
            path = os.path.abspath(os.path.join(os.path.dirname(__file__), "saved_models", "cost_model.pkl"))
        if not os.path.exists(path):
            raise FileNotFoundError(f"Saved model file not found at {path}")
            
        data = joblib.load(path)
        self.model = data["model"]
        self.waste_cluster_id = data["waste_cluster_id"]
        self.feature_columns = data["feature_columns"]
        print(f"Analytics [Cost]: Model loaded from {path}")
        return self

if __name__ == "__main__":
    conn = get_connection()
    model = CostWasteModel()
    model.train(conn)
    preds = model.predict(conn)
    print(preds.head())
    conn.close()
