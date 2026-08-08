import os
import json
import joblib
import numpy as np
from typing import Dict, Any, Tuple, Optional
from ml.ingestion.prometheus_client import FEATURE_COLUMNS
from shared.logging import get_logger

logger = get_logger("ml-anomaly-detector")


class AnomalyDetector:
    """
    Inference detector loading serialized Isolation Forest model
    and calculating normalized anomaly score [0.0 - 1.0].
    """
    def __init__(self, model_dir: str = "ml/models"):
        self.model_path = os.path.join(model_dir, "isolation_forest.pkl")
        self.scaler_path = os.path.join(model_dir, "scaler.pkl")
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
            is_anomaly (bool): True if score > threshold (0.75)
        """
        # Extract features in strict order
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
            if latency > 1.0 or error_rate > 0.15:
                anomaly_score = 0.90
            else:
                anomaly_score = 0.05

        is_anomaly = anomaly_score >= 0.75
        return anomaly_score, is_anomaly
