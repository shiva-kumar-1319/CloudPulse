import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseServiceSettings(BaseSettings):
    """
    Core environment configuration settings for CloudPulse microservices.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    ENVIRONMENT: str = "local"
    LOG_LEVEL: str = "INFO"

    # JWT Authentication
    JWT_SECRET: str = "super-secret-cloudpulse-key-change-in-production-32bytes"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Ports
    AUTH_SERVICE_PORT: int = 8001
    ORDER_SERVICE_PORT: int = 8002
    INVENTORY_SERVICE_PORT: int = 8003

    # Databases
    AUTH_DB_URL: str = "sqlite:///./auth_service.db"
    ORDER_DB_URL: str = "sqlite:///./order_service.db"
    INVENTORY_DB_URL: str = "sqlite:///./inventory_service.db"

    # Messaging
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    RABBITMQ_EXCHANGE: str = "cloudpulse.events"
    RABBITMQ_ORDER_CREATED_QUEUE: str = "inventory.order-created.queue"

    # Observability
    PROMETHEUS_URL: str = "http://localhost:9090"


settings = BaseServiceSettings()
