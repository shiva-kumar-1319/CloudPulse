from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class InventoryCreateRequest(BaseModel):
    product_id: str = Field(min_length=1, max_length=50, description="Product SKU / ID")
    product_name: str = Field(min_length=1, max_length=100, description="Product Name")
    stock_quantity: int = Field(ge=0, description="Initial stock quantity")


class InventoryUpdateRequest(BaseModel):
    stock_quantity: int = Field(ge=0, description="Updated stock quantity")


class StockReservationRequest(BaseModel):
    product_id: str
    quantity: int = Field(gt=0, description="Number of items to reserve")
    order_id: str


class StockReservationResponse(BaseModel):
    success: bool
    product_id: str
    order_id: str
    remaining_stock: int
    message: str


class InventoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: str
    product_name: str
    stock_quantity: int
    reserved_quantity: int = 0
    updated_at: datetime
