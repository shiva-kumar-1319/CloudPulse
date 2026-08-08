from fastapi import APIRouter
from shared.logging import get_metrics_response

router = APIRouter(tags=["Metrics"])


@router.get("/metrics")
@router.get("/inventory/metrics")
def metrics():
    return get_metrics_response()
