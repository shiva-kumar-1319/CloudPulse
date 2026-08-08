import httpx
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from shared.config.settings import settings
from shared.logging import get_logger

logger = get_logger("ml-metrics-ingestion")

FEATURE_COLUMNS = [
    "latency_mean",
    "latency_p95",
    "error_rate",
    "request_rate",
    "cpu_usage",
    "memory_usage",
    "pod_restarts"
]


class PrometheusMetricsIngestor:
    """
    Ingestion client that queries Prometheus metrics for target microservices
    and extracts feature vectors for anomaly detection.
    """
    def __init__(self, prometheus_url: str = settings.PROMETHEUS_URL):
        self.prometheus_url = prometheus_url.rstrip("/")

    async def fetch_metric_value(self, query: str) -> float:
        """
        Execute instant PromQL query against Prometheus API.
        """
        url = f"{self.prometheus_url}/api/v1/query"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url, params={"query": query})
                if response.status_code == 200:
                    data = response.json()
                    result = data.get("data", {}).get("result", [])
                    if result:
                        val = result[0].get("value", [None, "0"])[1]
                        return float(val) if val != "NaN" else 0.0
        except Exception as err:
            logger.debug(f"Prometheus query failed ('{query}'): {err}")
        return 0.0

    async def extract_service_features(self, service_name: str) -> Dict[str, float]:
        """
        Extract the 7 core feature metrics for a specific microservice.
        """
        queries = {
            "latency_mean": f'rate(http_request_duration_seconds_sum{{service="{service_name}"}}[1m]) / clamp_min(rate(http_request_duration_seconds_count{{service="{service_name}"}}[1m]), 0.001)',
            "latency_p95": f'histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{{service="{service_name}"}}[1m])) by (le))',
            "error_rate": f'sum(rate(http_requests_errors_total{{service="{service_name}"}}[1m])) / clamp_min(sum(rate(http_requests_total{{service="{service_name}"}}[1m])), 0.001)',
            "request_rate": f'sum(rate(http_requests_total{{service="{service_name}"}}[1m]))',
            "cpu_usage": f'process_cpu_seconds_total{{service="{service_name}"}}',
            "memory_usage": f'process_resident_memory_bytes{{service="{service_name}"}}',
            "pod_restarts": f'sum(kube_pod_container_status_restarts_total{{pod=~"{service_name}.*"}})'
        }

        feature_vector: Dict[str, float] = {}
        for feature, query in queries.items():
            val = await self.fetch_metric_value(query)
            feature_vector[feature] = float(np.nan_to_num(val, nan=0.0, posinf=0.0, neginf=0.0))

        return feature_vector
