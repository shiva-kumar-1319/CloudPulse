from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class OrderCreateRequest(BaseModel):
    product_id: str = Field(min_length=1, description="Target product SKU/ID")
    quantity: int = Field(gt=0, description="Quantity to purchase, must be > 0")
    idempotency_key: Optional[str] = Field(None, description="Unique client key to prevent duplicate orders")


class OrderCancelRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=255, description="Reason for order cancellation")


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    product_id: str
    quantity: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class OrderEventPayload(BaseModel):
    event_id: str
    event_type: str = "order.created"
    order_id: str
    user_id: str
    product_id: str
    quantity: int
    timestamp: datetime
