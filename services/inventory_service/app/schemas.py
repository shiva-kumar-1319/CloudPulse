from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class InventoryCreateRequest(BaseModel):
    product_id: str = Field(min_length=1, max_length=50, description="Product SKU / ID")
    product_name: str = Field(min_length=1, max_length=100, description="Product Name")
    stock_quantity: int = Field(ge=0, description="Initial stock quantity")


class InventoryUpdateRequest(BaseModel):
    stock_quantity: int = Field(ge=0, description="Updated stock quantity")


class InventoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: str
    product_name: str
    stock_quantity: int
    updated_at: datetime
