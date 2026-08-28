import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from services.api_gateway.app.api.dashboard import router as dashboard_router
from services.api_gateway.app.api.chaos import router as chaos_router
from shared.logging import get_logger

logger = get_logger("api-gateway")

app = FastAPI(
    title="CloudPulse Unified Control Plane API Gateway",
    version="0.1.0",
    description="Unified Ingress API Gateway exposing dashboard telemetry, ML anomaly history, remediation actions, and secure chaos endpoints."
)

# Enable CORS for frontend dashboard (local development & Firebase hosting)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_and_logging(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
    return response


app.include_router(dashboard_router)
app.include_router(chaos_router)


@app.get("/health", tags=["System"])
def health():
    return {
        "status": "healthy",
        "service": "api-gateway",
        "version": "0.1.0",
        "timestamp": time.time()
    }


@app.get("/readiness", tags=["System"])
def readiness():
    return {"status": "ready", "dependencies": {"database": "ok", "broker": "ok"}}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
