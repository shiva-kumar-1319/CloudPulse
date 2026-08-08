from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from services.inventory_service.app.database import get_db
from shared.schemas.health import HealthResponse, ComponentHealth

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
@router.get("/health/live", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        service="inventory-service",
        status="healthy",
        dependencies={
            "process": ComponentHealth(status="healthy")
        }
    )


@router.get("/health/ready", response_model=HealthResponse)
def readiness_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return HealthResponse(
            service="inventory-service",
            status="healthy",
            dependencies={
                "database": ComponentHealth(status="healthy", details={"engine": "connected"})
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=HealthResponse(
                service="inventory-service",
                status="unhealthy",
                dependencies={
                    "database": ComponentHealth(status="unhealthy", details={"error": str(e)})
                }
            ).model_dump()
        )
