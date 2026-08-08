from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field


class OrderCreatedEvent(BaseModel):
    """
    Schema for order-created events published to RabbitMQ.
    """
    event_id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4()}")
    event_type: str = "order-created"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    order_id: str
    user_id: str
    product_id: str
    quantity: int = Field(gt=0, description="Quantity ordered, must be > 0")
