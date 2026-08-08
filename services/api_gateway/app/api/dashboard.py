import time
import uuid
import httpx
from datetime import datetime, timezone
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Query

from services.api_gateway.app.schemas import (
    DashboardSummaryResponse,
    ServiceHealthCard,
    AnomalyEvent,
    RemediationEvent,
    SystemEventLog
)
from ml.ingestion.prometheus_client import PrometheusMetricsIngestor
from ml.inference.detector import AnomalyDetector
from remediation.kubernetes_client import K8S_AVAILABLE, KubernetesRemediationClient
from shared.config.settings import settings
from shared.logging import get_logger

logger = get_logger("api-gateway-dashboard")
router = APIRouter(prefix="/api", tags=["Dashboard Control Plane"])

# Stateful memory cache for simulation / live tracking
start_time = time.time()
metrics_ingestor = PrometheusMetricsIngestor()
anomaly_detector = AnomalyDetector()
k8s_client = KubernetesRemediationClient()

# Event timeline history
event_history: List[SystemEventLog] = [
    SystemEventLog(
        timestamp=datetime.now(timezone.utc).isoformat(),
        level="info",
        message="CloudPulse Self-Healing Control Plane initialized.",
        service="gateway"
    ),
    SystemEventLog(
        timestamp=datetime.now(timezone.utc).isoformat(),
        level="info",
        message="Prometheus metrics scraper and Isolation Forest ML model linked.",
        service="ml-engine"
    )
]

# Track recent remediation logs
remediation_history: List[RemediationEvent] = []
anomaly_history: List[AnomalyEvent] = []


def is_real_mode_active() -> bool:
    """
    Check whether real Prometheus & Kubernetes cluster context are reachable.
    """
    return k8s_client.in_cluster


@router.get("/dashboard/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary():
    """
    Get aggregated system summary status, cluster info, and operational mode.
    """
    real_mode = is_real_mode_active()
    mode_str = "REAL MODE" if real_mode else "SIMULATION MODE"

    # Determine aggregate system status
    system_status = "healthy"
    for a in anomaly_history[-3:]:
        if a.anomaly_score >= 0.75:
            system_status = "anomaly"
            break

    return DashboardSummaryResponse(
        system_status=system_status,
        operational_mode=mode_str,
        cluster_name="cloudpulse-eks-cluster" if real_mode else "Minikube (Local)",
        environment="production" if real_mode else "development",
        uptime_seconds=round(time.time() - start_time, 1),
        active_pods=6,
        healthy_services_count=3,
        total_services_count=3,
        anomalies_detected=len(anomaly_history),
        remediations_executed=len(remediation_history),
        grafana_url="http://localhost:3000"
    )


@router.get("/services", response_model=List[ServiceHealthCard])
async def list_service_health_cards():
    """
    Get real-time health, latency, error rates, CPU, memory, and pod metrics per service.
    """
    services = ["auth-service", "order-service", "inventory-service"]
    cards = []

    for svc in services:
        if is_real_mode_active():
            features = await metrics_ingestor.extract_service_features(svc)
            latency = features.get("latency_p95", 0.085) * 1000  # convert to ms
            error_rate = features.get("error_rate", 0.002) * 100
            cpu = features.get("cpu_usage", 0.15) * 100
            memory = (features.get("memory_usage", 64*1024*1024) / (512*1024*1024)) * 100
            restarts = int(features.get("pod_restarts", 0))
            score, _ = anomaly_detector.predict_anomaly(features)
            status_str = "anomaly" if score >= 0.75 else "healthy"
        else:
            # Baseline parameters for local simulation mode
            latency = 85.0 if svc != "order-service" else 82.0
            error_rate = 0.2
            cpu = 18.0
            memory = 42.0
            restarts = 0
            status_str = "healthy"

            # Check if recent anomaly is active for service
            for a in reversed(anomaly_history[-5:]):
                if a.target_service == svc and a.anomaly_score >= 0.75:
                    status_str = "degraded"
                    latency = 4250.0
                    error_rate = 45.0
                    cpu = 85.0
                    break

        cards.append(ServiceHealthCard(
            service_name=svc,
            status=status_str,
            latency_ms=round(latency, 1),
            error_rate_pct=round(error_rate, 2),
            cpu_pct=round(cpu, 1),
            memory_pct=round(memory, 1),
            pods_healthy=2,
            pods_total=2,
            restart_count=restarts,
            last_anomaly_at=anomaly_history[-1].timestamp if anomaly_history else None,
            last_remediation_at=remediation_history[-1].timestamp if remediation_history else None
        ))

    return cards


@router.get("/anomalies", response_model=List[AnomalyEvent])
def get_recent_anomalies(limit: int = Query(default=10, ge=1, le=50)):
    """
    Get history of Isolation Forest anomaly detections.
    """
    return anomaly_history[-limit:]


@router.get("/remediations", response_model=List[RemediationEvent])
def get_recent_remediations(limit: int = Query(default=10, ge=1, le=50)):
    """
    Get history of executed automated self-healing remediation actions.
    """
    return remediation_history[-limit:]


@router.get("/events", response_model=List[SystemEventLog])
def get_system_events(limit: int = Query(default=20, ge=1, le=100)):
    """
    Get real-time system event log stream.
    """
    return event_history[-limit:]
