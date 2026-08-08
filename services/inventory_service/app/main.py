import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from services.inventory_service.app.database import init_db
from services.inventory_service.app.api.inventory import router as inventory_router
from services.inventory_service.app.api.health import router as health_router
from services.inventory_service.app.api.metrics import router as metrics_router
from services.inventory_service.app.consumer import start_inventory_consumer
from shared.messaging import RabbitMQClient
from shared.logging import PrometheusMiddleware, get_logger

logger = get_logger("inventory-service")
rabbitmq_client = RabbitMQClient()
consumer_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global consumer_task
    logger.info("Initializing Inventory Service database...")
    init_db()
    # Connect RabbitMQ and start background consumer task
    connected = await rabbitmq_client.connect()
    if connected:
        consumer_task = asyncio.create_task(start_inventory_consumer(rabbitmq_client))
        logger.info("Started background RabbitMQ inventory consumer task.")
    else:
        logger.warning("RabbitMQ connection offline on startup. Service running in API mode.")

    logger.info("Inventory Service started successfully.")
    yield
    if consumer_task and not consumer_task.done():
        consumer_task.cancel()
    await rabbitmq_client.close()
    logger.info("Inventory Service shutting down.")


app = FastAPI(
    title="CloudPulse Inventory Service",
    version="0.1.0",
    description="Product Stock and Inventory Management Service",
    lifespan=lifespan
)

app.add_middleware(PrometheusMiddleware, service_name="inventory-service")

app.include_router(inventory_router)
app.include_router(health_router)
app.include_router(metrics_router)


if __name__ == "__main__":
    import uvicorn
    from shared.config.settings import settings
    uvicorn.run(app, host="0.0.0.0", port=settings.INVENTORY_SERVICE_PORT)
