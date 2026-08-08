from contextlib import asynccontextmanager
from fastapi import FastAPI
from services.auth_service.app.database import init_db
from services.auth_service.app.api.auth import router as auth_router
from services.auth_service.app.api.health import router as health_router
from services.auth_service.app.api.metrics import router as metrics_router
from shared.logging import PrometheusMiddleware, get_logger

logger = get_logger("auth-service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Auth Service database...")
    init_db()
    logger.info("Auth Service started successfully.")
    yield
    logger.info("Auth Service shutting down.")


app = FastAPI(
    title="CloudPulse Auth Service",
    version="0.1.0",
    description="Authentication and Identity Management Service",
    lifespan=lifespan
)

# Prometheus Middleware
app.add_middleware(PrometheusMiddleware, service_name="auth-service")

# Include Routers
app.include_router(auth_router)
app.include_router(health_router)
app.include_router(metrics_router)


if __name__ == "__main__":
    import uvicorn
    from shared.config.settings import settings
    uvicorn.run(app, host="0.0.0.0", port=settings.AUTH_SERVICE_PORT)
