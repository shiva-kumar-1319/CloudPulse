from contextlib import asynccontextmanager
from fastapi import FastAPI
from services.order_service.app.database import init_db
from services.order_service.app.api.orders import router as order_router, rabbitmq_client
from services.order_service.app.api.health import router as health_router
from services.order_service.app.api.metrics import router as metrics_router
from shared.logging import PrometheusMiddleware, get_logger

logger = get_logger("order-service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Order Service database...")
    init_db()
    # Connect RabbitMQ client
    await rabbitmq_client.connect()
    logger.info("Order Service started successfully.")
    yield
    await rabbitmq_client.close()
    logger.info("Order Service shutting down.")


app = FastAPI(
    title="CloudPulse Order Service",
    version="0.1.0",
    description="Order Creation & Management Service",
    lifespan=lifespan
)

app.add_middleware(PrometheusMiddleware, service_name="order-service")

app.include_router(order_router)
app.include_router(health_router)
app.include_router(metrics_router)


if __name__ == "__main__":
    import uvicorn
    from shared.config.settings import settings
    uvicorn.run(app, host="0.0.0.0", port=settings.ORDER_SERVICE_PORT)
