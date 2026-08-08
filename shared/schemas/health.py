from typing import Dict, Any, Optional
from pydantic import BaseModel


class ComponentHealth(BaseModel):
    status: str  # "healthy", "degraded", "unhealthy"
    details: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    service: str
    status: str  # "healthy" or "unhealthy"
    version: str = "0.1.0"
    dependencies: Optional[Dict[str, ComponentHealth]] = None
