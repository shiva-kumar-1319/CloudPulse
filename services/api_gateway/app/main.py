from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.api_gateway.app.api.dashboard import router as dashboard_router
from services.api_gateway.app.api.chaos import router as chaos_router
from shared.logging import get_logger

logger = get_logger("api-gateway")

app = FastAPI(
    title="CloudPulse Unified Control Plane API Gateway",
    version="0.1.0",
    description="Unified API Gateway exposing dashboard telemetry, ML anomaly history, remediation actions, and secure chaos endpoints."
)

# Enable CORS for React frontend (Vite dev server + production domains)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits local React dev server and hosted domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard_router)
app.include_router(chaos_router)


@app.get("/health")
def health():
    return {"status": "healthy", "service": "api-gateway", "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
