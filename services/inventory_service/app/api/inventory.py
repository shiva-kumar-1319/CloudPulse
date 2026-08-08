from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from services.inventory_service.app.database import get_db
from services.inventory_service.app.models import InventoryItem
from services.inventory_service.app.schemas import (
    InventoryCreateRequest,
    InventoryUpdateRequest,
    InventoryResponse
)
from shared.logging import get_logger

logger = get_logger("inventory-service")
router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.post("", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
def create_inventory_item(payload: InventoryCreateRequest, db: Session = Depends(get_db)):
    """
    Create a new inventory item stock record.
    """
    existing = db.get(InventoryItem, payload.product_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Inventory record for product '{payload.product_id}' already exists."
        )

    item = InventoryItem(
        product_id=payload.product_id,
        product_name=payload.product_name,
        stock_quantity=payload.stock_quantity
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    logger.info(f"Created inventory item: {item.product_id} with stock {item.stock_quantity}")
    return item


@router.get("/{product_id}", response_model=InventoryResponse)
def get_inventory_item(product_id: str, db: Session = Depends(get_db)):
    """
    Get inventory stock details for a product.
    """
    item = db.get(InventoryItem, product_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Product '{product_id}' not found in inventory")
    return item


@router.patch("/{product_id}", response_model=InventoryResponse)
def update_inventory_stock(
    product_id: str,
    payload: InventoryUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Update stock quantity for a product.
    """
    item = db.get(InventoryItem, product_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Product '{product_id}' not found in inventory")

    item.stock_quantity = payload.stock_quantity
    db.commit()
    db.refresh(item)

    logger.info(f"Updated inventory item {product_id} stock to {item.stock_quantity}")
    return item


@router.get("", response_model=List[InventoryResponse])
def list_inventory_items(db: Session = Depends(get_db)):
    """
    List all inventory stock records.
    """
    stmt = select(InventoryItem)
    items = db.scalars(stmt).all()
    return items
