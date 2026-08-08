from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from services.order_service.app.database import get_db
from services.order_service.app.models import Order
from services.order_service.app.schemas import OrderCreateRequest, OrderResponse
from shared.auth import get_current_user_id
from shared.schemas import OrderCreatedEvent
from shared.messaging import RabbitMQClient
from shared.logging import get_logger

logger = get_logger("order-service")
router = APIRouter(prefix="/orders", tags=["Orders"])

# RabbitMQ Client Instance
rabbitmq_client = RabbitMQClient()


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreateRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Create a new order for the authenticated user and publish `order-created` event.
    """
    order = Order(
        user_id=user_id,
        product_id=payload.product_id,
        quantity=payload.quantity,
        status="PENDING"
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    logger.info(f"Created order {order.id} for user {user_id}")

    # Build and publish order-created event schema
    event = OrderCreatedEvent(
        order_id=order.id,
        user_id=order.user_id,
        product_id=order.product_id,
        quantity=order.quantity
    )

    published = await rabbitmq_client.publish(
        routing_key="order.created",
        message_data=event.model_dump()
    )

    if not published:
        logger.warning(f"Order {order.id} saved in DB but RabbitMQ event publishing failed/fallback mode.")

    return order


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retrieve order details by order_id.
    """
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access forbidden: order belongs to another user")

    return order


@router.get("", response_model=List[OrderResponse])
def list_orders(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    List all orders for the currently authenticated user.
    """
    stmt = select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
    orders = db.scalars(stmt).all()
    return orders
