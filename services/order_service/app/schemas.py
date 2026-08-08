from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class OrderCreateRequest(BaseModel):
    product_id: str = Field(min_length=1, description="Target product SKU/ID")
    quantity: int = Field(gt=0, description="Quantity to purchase, must be > 0")


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    product_id: str
    quantity: int
    status: str
    created_at: datetime
