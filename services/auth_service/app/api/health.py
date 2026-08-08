from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from services.auth_service.app.database import get_db
from shared.schemas.health import HealthResponse, ComponentHealth

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
@router.get("/health/live", response_model=HealthResponse)
def health_check():
    """
    Liveness probe: verifies service runtime process is running.
    """
    return HealthResponse(
        service="auth-service",
        status="healthy",
        dependencies={
            "process": ComponentHealth(status="healthy")
        }
    )


@router.get("/health/ready", response_model=HealthResponse)
def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness probe: verifies database dependency is ready to serve requests.
    """
    try:
        db.execute(text("SELECT 1"))
        return HealthResponse(
            service="auth-service",
            status="healthy",
            dependencies={
                "database": ComponentHealth(status="healthy", details={"engine": "connected"})
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=HealthResponse(
                service="auth-service",
                status="unhealthy",
                dependencies={
                    "database": ComponentHealth(status="unhealthy", details={"error": str(e)})
                }
            ).model_dump()
        )
