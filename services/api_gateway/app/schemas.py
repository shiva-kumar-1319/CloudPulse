from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class DashboardSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    system_status: str  # "healthy", "degraded", "anomaly"
    operational_mode: str  # "REAL MODE" or "SIMULATION MODE"
    cluster_name: str
    environment: str
    uptime_seconds: float
    active_pods: int
    healthy_services_count: int
    total_services_count: int
    anomalies_detected: int
    remediations_executed: int
    grafana_url: str = "http://localhost:3000"


class ServiceHealthCard(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    service_name: str
    status: str  # "healthy", "degraded", "unhealthy", "unknown"
    latency_ms: float
    error_rate_pct: float
    cpu_pct: float
    memory_pct: float
    pods_healthy: int
    pods_total: int
    restart_count: int
    last_anomaly_at: Optional[str] = None
    last_remediation_at: Optional[str] = None


class AnomalyEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    target_service: str
    anomaly_score: float
    status: str  # "HEALTHY", "DEGRADATION DETECTED"
    timestamp: str
    feature_contributions: Dict[str, str]
    model_version: str = "Isolation Forest v1"


class RemediationEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    target_service: str
    action: str
    reason: str
    anomaly_score: float
    timestamp: str
    status: str
    recovery_time_seconds: int


class SystemEventLog(BaseModel):
    timestamp: str
    level: str  # "info", "warning", "danger", "success"
    message: str
    service: Optional[str] = None


class ChaosPodRequest(BaseModel):
    target_service: str = Field(description="Target microservice name")
    namespace: str = Field(default="cloudpulse", description="Target Kubernetes namespace")
    dry_run: bool = Field(default=False, description="Preview fault injection without executing")


class ChaosLatencyRequest(BaseModel):
    target_service: str = Field(description="Target microservice name")
    seconds: float = Field(default=3.5, gt=0, description="Latency delay in seconds")
    dry_run: bool = Field(default=False, description="Preview fault injection without executing")


class ChaosErrorRequest(BaseModel):
    target_service: str = Field(description="Target microservice name")
    rate: float = Field(default=0.5, ge=0.0, le=1.0, description="HTTP 500 error rate (0.0 to 1.0)")
    dry_run: bool = Field(default=False, description="Preview fault injection without executing")
