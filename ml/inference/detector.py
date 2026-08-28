import os
import json
import joblib
import numpy as np
from typing import Dict, Any, Tuple, Optional, List
from ml.ingestion.prometheus_client import FEATURE_COLUMNS
from shared.logging import get_logger

logger = get_logger("ml-anomaly-detector")


class AnomalyDetector:
    """
    Inference detector loading serialized Isolation Forest model
    and calculating normalized anomaly score [0.0 - 1.0] with feature attribution.
    """
    def __init__(self, model_dir: str = "ml/models", threshold: float = 0.75):
        self.model_path = os.path.join(model_dir, "isolation_forest.pkl")
        self.scaler_path = os.path.join(model_dir, "scaler.pkl")
        self.threshold = threshold
        self.model = None
        self.scaler = None
        self.load_model()

    def load_model(self) -> bool:
        """
        Load trained Isolation Forest and Scaler objects.
        """
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            try:
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                logger.info(f"Loaded trained ML Isolation Forest model from {self.model_path}")
                return True
            except Exception as exc:
                logger.error(f"Error loading ML model artifacts: {exc}")
        else:
            logger.warning("ML model files missing. Inference running in fallback baseline mode.")
        return False

    def predict_anomaly(self, feature_vector: Dict[str, float]) -> Tuple[float, bool]:
        """
        Calculate anomaly score and anomaly status.
        Returns:
            anomaly_score (float): Normalized score [0.0 = Healthy, 1.0 = Anomaly]
            is_anomaly (bool): True if score >= threshold (0.75)
        """
        raw_values = [feature_vector.get(col, 0.0) for col in FEATURE_COLUMNS]
        X = np.array(raw_values).reshape(1, -1)

        if self.model and self.scaler:
            X_scaled = self.scaler.transform(X)
            # IsolationForest decision_function: positive = inlier, negative = outlier
            decision_score = self.model.decision_function(X_scaled)[0]
            # Convert decision score to normalized 0.0 - 1.0 probability
            anomaly_score = float(np.clip(0.5 - (decision_score * 2.5), 0.0, 1.0))
        else:
            # Rule-based fallback if ML model is uninitialized
            latency = feature_vector.get("latency_mean", 0.0)
            error_rate = feature_vector.get("error_rate", 0.0)
            cpu = feature_vector.get("cpu_usage", 0.0)
            if latency > 1.0 or error_rate > 0.15 or cpu > 1.5:
                anomaly_score = 0.92
            else:
                anomaly_score = 0.08

        is_anomaly = anomaly_score >= self.threshold
        return anomaly_score, is_anomaly

    def explain_anomaly(self, feature_vector: Dict[str, float]) -> Dict[str, float]:
        """
        Generate feature contribution breakdown for telemetry explainability.
        """
        weights = {}
        raw_values = {col: feature_vector.get(col, 0.0) for col in FEATURE_COLUMNS}
        
        # Calculate individual metric z-scores/relative deviations
        latency_p95 = raw_values.get("latency_p95", 0.0)
        error_rate = raw_values.get("error_rate", 0.0)
        cpu_usage = raw_values.get("cpu_usage", 0.0)
        pod_restarts = raw_values.get("pod_restarts", 0.0)

        total_deviation = (latency_p95 * 2.0) + (error_rate * 50.0) + (cpu_usage * 1.5) + (pod_restarts * 10.0) + 0.001
        
        weights["latency_p95"] = round((latency_p95 * 2.0) / total_deviation, 3)
        weights["error_rate"] = round((error_rate * 50.0) / total_deviation, 3)
        weights["cpu_usage"] = round((cpu_usage * 1.5) / total_deviation, 3)
        weights["pod_restarts"] = round((pod_restarts * 10.0) / total_deviation, 3)

        return weights
