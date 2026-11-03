import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from warehouse.db_connection import get_connection

class AnomalyDetector:
    """
    Multi-Modal Anomaly Detector combining:
    1. Isolation Forest on time-series telemetry features (CPU, memory, network).
    2. Contextual / Operational Threat Scorer on dynamic alerts and configuration changes.

    Produces distinct sub-scores:
    - telemetry_anomaly_score: 0-100 score from Isolation Forest via logistic calibration.
    - contextual_anomaly_score: 0-100 score from dynamic security/operational alerts.
    - anomaly_score: combined score (np.maximum) for risk pipeline backward compatibility.
    - is_anomaly: boolean classification based on calibrated decision threshold (default: 65.0).
    """
    def __init__(self, n_estimators: int = 100, contamination: float = 0.04, random_state: int = 42,
                 decision_threshold: float = 65.0, logistic_k: float = 30.0, logistic_shift: float = 0.010):
        self.model = IsolationForest(
            n_estimators=n_estimators,
            contamination=contamination,
            random_state=random_state
        )
        self.feature_columns = None
        self.cached_features = None
        self.decision_threshold = decision_threshold
        self.logistic_k = logistic_k
        self.logistic_shift = logistic_shift

    def _build_telemetry_features(self, conn) -> pd.DataFrame:
        """
        Extracts daily metrics and computes time-series statistical features per instance.

        Engineered features:
        - Robust z-scores (CPU, memory, network): outlier deviation using median and MAD.
        - Day-to-day absolute differences (CPU, memory, network): captures abrupt single-day spikes.
        - Peak-to-median ratios (CPU, network): captures burstiness over baseline.
        - 7-day vs. 30-day deviation (CPU, memory): captures trend divergences across temporal scales.
        - Rolling 5-day memory slope: captures gradual linear memory ramps (memory leaks).
        - Memory-CPU divergence (mem - cpu): separates memory-specific accumulation from compute load.

        Parameters:
            conn (duckdb.DuckDBPyConnection): Active DuckDB connection.

        Returns:
            pd.DataFrame: Engineered telemetry features indexed by instance_id.
        """
        if self.cached_features is not None:
            return self.cached_features

        query = """
            SELECT instance_id, date, cpu_utilization_pct, memory_utilization_pct, network_out_mb
            FROM metrics_daily
            ORDER BY instance_id, date
        """
        metrics_df = conn.execute(query).fetchdf()

        telemetry_records = []
        for inst_id, group in metrics_df.groupby("instance_id"):
            cpu = group["cpu_utilization_pct"].values
            mem = group["memory_utilization_pct"].values
            net = group["network_out_mb"].values

            # --- CPU Time-Series Features ---
            c_med = float(np.median(cpu))
            c_mad = float(np.median(np.abs(cpu - c_med)))
            cpu_robust_z_max = float(np.max((cpu - c_med) / (1.4826 * c_mad + 1e-5)))
            cpu_day_diff_max = float(np.max(np.abs(np.diff(cpu)))) if len(cpu) > 1 else 0.0
            cpu_peak_to_median = float(np.max(cpu) / (c_med + 1.0))
            s_cpu = pd.Series(cpu)
            cpu_7_vs_30_dev_max = float(np.max(np.abs(
                s_cpu.rolling(7, min_periods=1).mean() - s_cpu.rolling(30, min_periods=1).mean()
            )))

            # --- Memory Time-Series Features ---
            m_med = float(np.median(mem))
            m_mad = float(np.median(np.abs(mem - m_med)))
            mem_robust_z_max = float(np.max((mem - m_med) / (1.4826 * m_mad + 1e-5)))
            mem_day_diff_max = float(np.max(np.abs(np.diff(mem)))) if len(mem) > 1 else 0.0
            mem_peak_to_median = float(np.max(mem) / (m_med + 1.0))
            s_mem = pd.Series(mem)
            mem_7_vs_30_dev_max = float(np.max(np.abs(
                s_mem.rolling(7, min_periods=1).mean() - s_mem.rolling(30, min_periods=1).mean()
            )))

            # Linear regression slope kernel over rolling 5-day window: [-2, -1, 0, 1, 2] / 10
            kernel = np.array([-2.0, -1.0, 0.0, 1.0, 2.0]) / 10.0
            mem_slopes = np.convolve(mem, kernel, mode="valid")
            mem_rolling_slope_max = float(np.max(mem_slopes)) if len(mem_slopes) > 0 else 0.0
            mem_minus_cpu_max = float(np.max(mem - cpu))

            # --- Network Time-Series Features ---
            n_med = float(np.median(net))
            n_mad = float(np.median(np.abs(net - n_med)))
            net_robust_z_max = float(np.max((net - n_med) / (1.4826 * n_mad + 1e-5)))
            net_day_diff_max = float(np.max(np.abs(np.diff(net)))) if len(net) > 1 else 0.0
            net_peak_to_median = float(np.max(net) / (n_med + 1.0))

            telemetry_records.append({
                "instance_id": inst_id,
                "cpu_robust_z_max": cpu_robust_z_max,
                "cpu_day_diff_max": cpu_day_diff_max,
                "cpu_peak_to_median": cpu_peak_to_median,
                "cpu_7_vs_30_dev_max": cpu_7_vs_30_dev_max,
                "mem_robust_z_max": mem_robust_z_max,
                "mem_day_diff_max": mem_day_diff_max,
                "mem_rolling_slope_max": mem_rolling_slope_max,
                "mem_minus_cpu_max": mem_minus_cpu_max,
                "net_robust_z_max": net_robust_z_max,
                "net_day_diff_max": net_day_diff_max,
                "net_peak_to_median": net_peak_to_median,
            })

        features_df = pd.DataFrame(telemetry_records).set_index("instance_id")
        self.cached_features = features_df
        return features_df

    def _build_features(self, conn) -> pd.DataFrame:
        """Alias for _build_telemetry_features for backward compatibility."""
        return self._build_telemetry_features(conn)

    def calculate_contextual_anomaly(self, conn) -> pd.DataFrame:
        """
        Evaluates dynamic threat events and configuration-change signals.

        Contextual signals:
        - Unauthorized access attempt events (brute force attacks): +70 points.
        - High volume / sudden burst in failed logins (failed_logins_7d > 25): +20 points (+10 if > 10).
        - Dynamic port exposure on an internet-exposed perimeter host (independent of port number): +65 points.
        - High or critical operational alerts (e.g. CPU runaway saturation or data exfiltration): +65 points.

        Returns:
            pd.DataFrame: Indexed by instance_id with contextual_anomaly_score in [0.0, 100.0].
        """
        query = """
            SELECT 
                sc.instance_id,
                sc.internet_exposed,
                sc.open_ports,
                sc.failed_logins_7d,
                COALESCE(SUM(CASE WHEN se.event_type = 'unauthorized_access_attempt' THEN 1 ELSE 0 END), 0) AS unauth_count,
                COALESCE(SUM(CASE WHEN se.event_type = 'port_opened' THEN 1 ELSE 0 END), 0) AS port_opened_count,
                COALESCE(SUM(CASE WHEN se.event_type = 'anomalous_traffic' AND se.severity IN ('high', 'critical') THEN 1 ELSE 0 END), 0) AS high_traffic_alerts
            FROM security_configurations sc
            LEFT JOIN security_events se ON sc.instance_id = se.instance_id
            GROUP BY sc.instance_id, sc.internet_exposed, sc.open_ports, sc.failed_logins_7d
        """
        sec_df = conn.execute(query).fetchdf().set_index("instance_id")

        scores = []
        for inst_id, row in sec_df.iterrows():
            c_score = 0.0

            # Signal 1: Unauthorized access attempts
            if row["unauth_count"] > 0:
                c_score += 70.0

            # Signal 2: Surge in failed authentication attempts
            logins = row["failed_logins_7d"]
            if logins > 25:
                c_score += 20.0
            elif logins > 10:
                c_score += 10.0

            # Signal 3: Dynamic port exposure on an internet-exposed host
            # Evaluates unapproved boundary modifications without hardcoding specific port numbers
            if row["port_opened_count"] > 0 and row["internet_exposed"]:
                c_score += 65.0

            # Signal 4: Acute high/critical operational alerts (e.g. CPU runaway saturation / exfiltration)
            if row["high_traffic_alerts"] > 0:
                c_score += 65.0

            scores.append(min(100.0, c_score))

        sec_df["contextual_anomaly_score"] = scores
        return sec_df[["contextual_anomaly_score"]]

    def train(self, conn):
        """
        Builds telemetry features and fits the IsolationForest model.

        Parameters:
            conn (duckdb.DuckDBPyConnection): Active DuckDB connection.
        """
        print("Analytics [Anomaly]: Building time-series telemetry features...")
        features = self._build_telemetry_features(conn)
        self.feature_columns = list(features.columns)

        print("Analytics [Anomaly]: Training Isolation Forest model on telemetry features...")
        self.model.fit(features[self.feature_columns])
        return self

    def predict(self, conn) -> pd.DataFrame:
        """
        Computes multi-modal anomaly scores across telemetry and contextual signals.

        Parameters:
            conn (duckdb.DuckDBPyConnection): Active DuckDB connection.

        Returns:
            pd.DataFrame: Columns:
                - instance_id (str)
                - anomaly_score (float, 0-100): combined anomaly score.
                - telemetry_anomaly_score (float, 0-100): Isolation Forest score.
                - contextual_anomaly_score (float, 0-100): Security/event score.
                - is_anomaly (bool): True if anomaly_score >= decision_threshold.
        """
        if self.feature_columns is None:
            raise RuntimeError("Model must be trained or loaded before making predictions.")

        features = self._build_telemetry_features(conn)
        X = features[self.feature_columns]

        # 1. Isolation Forest decision function: decision < 0 indicates anomaly
        decision = self.model.decision_function(X)

        # Calibrate decision values to [0, 100] via logistic sigmoid anchored at decision threshold
        # score = 100 / (1 + exp(k * (decision - shift)))
        telemetry_score = 100.0 / (1.0 + np.exp(self.logistic_k * (decision - self.logistic_shift)))

        # 2. Contextual / Operational Threat Scoring
        df_contextual = self.calculate_contextual_anomaly(conn)
        contextual_score = df_contextual.loc[features.index, "contextual_anomaly_score"].values

        # 3. Multi-Modal Combination
        combined_score = np.maximum(telemetry_score, contextual_score)
        is_anom = combined_score >= self.decision_threshold

        output_df = pd.DataFrame({
            "instance_id": features.index,
            "anomaly_score": np.round(combined_score, 4),
            "telemetry_anomaly_score": np.round(telemetry_score, 4),
            "contextual_anomaly_score": np.round(contextual_score, 4),
            "is_anomaly": is_anom.astype(bool)
        })
        return output_df

    def save(self, path=None):
        """
        Saves the fitted model and configuration parameters using joblib.
        """
        if path is None:
            path = os.path.abspath(os.path.join(os.path.dirname(__file__), "saved_models", "anomaly_model.pkl"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            "model": self.model,
            "feature_columns": self.feature_columns,
            "decision_threshold": self.decision_threshold,
            "logistic_k": self.logistic_k,
            "logistic_shift": self.logistic_shift
        }, path)
        print(f"Analytics [Anomaly]: Model saved to {path}")

    def load(self, path=None):
        """
        Loads the model and configuration parameters from file using joblib.
        """
        if path is None:
            path = os.path.abspath(os.path.join(os.path.dirname(__file__), "saved_models", "anomaly_model.pkl"))
        if not os.path.exists(path):
            raise FileNotFoundError(f"Saved model file not found at {path}")

        data = joblib.load(path)
        self.model = data["model"]
        self.feature_columns = data["feature_columns"]
        self.decision_threshold = data.get("decision_threshold", 65.0)
        self.logistic_k = data.get("logistic_k", 30.0)
        self.logistic_shift = data.get("logistic_shift", 0.010)
        print(f"Analytics [Anomaly]: Model loaded from {path}")
        return self

if __name__ == "__main__":
    conn = get_connection()
    detector = AnomalyDetector()
    detector.train(conn)
    preds = detector.predict(conn)
    print(preds.head(10))
    print(f"\nTotal instances: {len(preds)}")
    print(f"Predicted anomalies (score >= {detector.decision_threshold}): {preds['is_anomaly'].sum()}")
    conn.close()
