import os
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from ml.ingestion.prometheus_client import FEATURE_COLUMNS
from shared.logging import get_logger

logger = get_logger("ml-training")


def generate_synthetic_dataset(num_samples: int = 2000, contamination_rate: float = 0.05) -> pd.DataFrame:
    """
    Generate synthetic time-series metric data modeling normal operation (95%)
    and anomalous chaos conditions (5%).
    """
    np.random.seed(42)
    num_anomalies = int(num_samples * contamination_rate)
    num_normal = num_samples - num_anomalies

    # Normal Operating Conditions (Baseline)
    normal_data = {
        "latency_mean": np.random.normal(loc=0.045, scale=0.015, size=num_normal).clip(min=0.005),
        "latency_p95": np.random.normal(loc=0.120, scale=0.035, size=num_normal).clip(min=0.020),
        "error_rate": np.random.uniform(low=0.0, high=0.01, size=num_normal),
        "request_rate": np.random.normal(loc=25.0, scale=5.0, size=num_normal).clip(min=1.0),
        "cpu_usage": np.random.normal(loc=0.15, scale=0.04, size=num_normal).clip(min=0.02),
        "memory_usage": np.random.normal(loc=64*1024*1024, scale=8*1024*1024, size=num_normal).clip(min=10*1024*1024),
        "pod_restarts": np.zeros(num_normal)
    }

    # Anomalous Conditions (Latencies spike to 3s+, error rates jump to 40%+, restarts increase)
    anomaly_data = {
        "latency_mean": np.random.uniform(low=1.5, high=6.0, size=num_anomalies),
        "latency_p95": np.random.uniform(low=3.0, high=10.0, size=num_anomalies),
        "error_rate": np.random.uniform(low=0.15, high=0.75, size=num_anomalies),
        "request_rate": np.random.uniform(low=0.5, high=150.0, size=num_anomalies),
        "cpu_usage": np.random.uniform(low=0.85, high=2.5, size=num_anomalies),
        "memory_usage": np.random.uniform(low=200*1024*1024, high=512*1024*1024, size=num_anomalies),
        "pod_restarts": np.random.choice([1, 2, 3, 5], size=num_anomalies)
    }

    df_normal = pd.DataFrame(normal_data)
    df_anomaly = pd.DataFrame(anomaly_data)

    df_combined = pd.concat([df_normal, df_anomaly], ignore_index=True)
    df_shuffled = df_combined.sample(frac=1.0, random_state=42).reset_index(drop=True)
    return df_shuffled


def train_model(output_dir: str = "ml/models"):
    """
    Train Isolation Forest model on metric feature vectors and serialize model artifacts.
    """
    os.makedirs(output_dir, exist_ok=True)
    data_dir = "ml/data"
    os.makedirs(data_dir, exist_ok=True)

    logger.info("Generating synthetic metrics dataset for model training...")
    df = generate_synthetic_dataset(num_samples=2000, contamination_rate=0.05)
    
    # Save CSV dataset for auditability
    csv_path = os.path.join(data_dir, "synthetic_metrics.csv")
    df.to_csv(csv_path, index=False)
    logger.info(f"Saved synthetic dataset to {csv_path}")

    X = df[FEATURE_COLUMNS].values

    # Fit Scaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train Isolation Forest with n_jobs=1
    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42,
        n_jobs=1
    )
    model.fit(X_scaled)

    # Save artifacts
    model_path = os.path.join(output_dir, "isolation_forest.pkl")
    scaler_path = os.path.join(output_dir, "scaler.pkl")
    metadata_path = os.path.join(output_dir, "model_metadata.json")

    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)

    metadata = {
        "model_type": "IsolationForest",
        "n_estimators": 100,
        "contamination": 0.05,
        "features": FEATURE_COLUMNS,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "num_samples": len(df)
    }

    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"Successfully trained and saved Isolation Forest model to {model_path}")


if __name__ == "__main__":
    train_model()
