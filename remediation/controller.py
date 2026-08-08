import uvicorn
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

from remediation.kubernetes_client import KubernetesRemediationClient
from remediation.policies import RemediationPolicyEngine
from shared.logging import get_logger

logger = get_logger("remediation-controller")

# Prometheus Counter metric for tracking self-healing interventions
REMEDIATION_ACTIONS_TOTAL = Counter(
    "cloudpulse_remediation_actions_total",
    "Total automated self-healing remediation actions executed",
    ["target_service", "action", "status"]
)


class AnomalyAlertRequest(BaseModel):
    target_service: str = Field(description="Target microservice name")
    anomaly_score: float = Field(ge=0.0, le=1.0, description="Anomaly confidence score")
    recommended_action: Optional[str] = "restart_pod"
    metrics: Optional[Dict[str, Any]] = None


class RemediationResponse(BaseModel):
    status: str
    target_service: str
    action_taken: str
    reason: str
    timestamp: str


policy_engine = RemediationPolicyEngine()
k8s_client = KubernetesRemediationClient()

app = FastAPI(
    title="CloudPulse Remediation Controller",
    version="0.1.0",
    description="Automated Self-Healing Kubernetes Remediation Controller"
)


@app.post("/remediation/alert", response_model=RemediationResponse)
async def receive_anomaly_alert(payload: AnomalyAlertRequest):
    """
    Receive ML anomaly alert and trigger self-healing Kubernetes remediation.
    """
    service = payload.target_service
    score = payload.anomaly_score
    action = payload.recommended_action or "restart_pod"

    logger.info(f"Received anomaly alert for service '{service}' (Score: {score:.2f})")

    # Evaluate Safety Guardrails
    allowed, reason = policy_engine.validate_action(service, score)

    if not allowed:
        logger.warning(f"Remediation BLOCKED for '{service}': {reason}")
        REMEDIATION_ACTIONS_TOTAL.labels(target_service=service, action=action, status="blocked").inc()
        return RemediationResponse(
            status="blocked",
            target_service=service,
            action_taken="none",
            reason=reason,
            timestamp=logger.handlers[0].formatter.formatTime(None) if logger.handlers else ""
        )

    # Execute Remediation Action
    success = False
    if action == "restart_pod":
        success = k8s_client.restart_pod(service)
    elif action == "scale_deployment":
        success = k8s_client.scale_deployment(service, target_replicas=3)

    if success:
        policy_engine.record_remediation(service)
        REMEDIATION_ACTIONS_TOTAL.labels(target_service=service, action=action, status="success").inc()
        logger.info(f"Successfully executed self-healing action '{action}' for service '{service}'")
        return RemediationResponse(
            status="success",
            target_service=service,
            action_taken=action,
            reason="Self-healing remediation executed successfully",
            timestamp=""
        )
    else:
        REMEDIATION_ACTIONS_TOTAL.labels(target_service=service, action=action, status="failed").inc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute remediation action '{action}' on service '{service}'"
        )


@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/health")
def health():
    return {"status": "healthy", "service": "remediation-controller"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)
