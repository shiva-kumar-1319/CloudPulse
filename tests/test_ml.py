import pytest
import numpy as np
from ml.training.train import generate_synthetic_dataset, train_model
from ml.inference.detector import AnomalyDetector


def test_synthetic_dataset_generation():
    df = generate_synthetic_dataset(num_samples=1000, contamination_rate=0.05)
    assert len(df) == 1000
    assert "latency_mean" in df.columns
    assert "error_rate" in df.columns


def test_model_training_and_inference():
    # Train model
    train_model(output_dir="ml/models")

    detector = AnomalyDetector(model_dir="ml/models")
    assert detector.model is not None
    assert detector.scaler is not None

    # Test normal feature vector (Healthy)
    normal_vector = {
        "latency_mean": 0.040,
        "latency_p95": 0.100,
        "error_rate": 0.001,
        "request_rate": 20.0,
        "cpu_usage": 0.10,
        "memory_usage": 60 * 1024 * 1024,
        "pod_restarts": 0.0
    }
    normal_score, is_normal_anomaly = detector.predict_anomaly(normal_vector)
    assert normal_score < 0.60
    assert is_normal_anomaly is False

    # Test extreme anomaly feature vector (Chaos Latency Spike + 50% Errors)
    anomaly_vector = {
        "latency_mean": 5.500,
        "latency_p95": 12.000,
        "error_rate": 0.550,
        "request_rate": 120.0,
        "cpu_usage": 2.10,
        "memory_usage": 400 * 1024 * 1024,
        "pod_restarts": 3.0
    }
    anomaly_score, is_anomaly = detector.predict_anomaly(anomaly_vector)
    assert anomaly_score >= 0.70
    assert is_anomaly is True
