import asyncio
from typing import Dict, Any
from sqlalchemy import select
from services.inventory_service.app.database import SessionLocal
from services.inventory_service.app.models import InventoryItem, ProcessedEvent
from shared.messaging import RabbitMQClient
from shared.config.settings import settings
from shared.logging import get_logger

logger = get_logger("inventory-consumer")


async def handle_order_created_event(payload: Dict[str, Any]) -> bool:
    """
    Idempotent consumer handler for `order-created` events.
    Reduces inventory stock level upon successful order placement.
    """
    event_id = payload.get("event_id")
    product_id = payload.get("product_id")
    quantity = payload.get("quantity", 0)
    order_id = payload.get("order_id")

    if not event_id or not product_id:
        logger.error(f"Malformed order-created event payload: {payload}")
        return True  # Acknowledge malformed message to remove from queue

    db = SessionLocal()
    try:
        # Check idempotency
        stmt_processed = select(ProcessedEvent).where(ProcessedEvent.event_id == event_id)
        already_processed = db.scalar(stmt_processed)

        if already_processed:
            logger.info(f"Skipping duplicate event {event_id} (already processed).")
            return True

        # Fetch product inventory
        item = db.get(InventoryItem, product_id)

        if not item:
            logger.warning(
                f"Product {product_id} not found in inventory for order {order_id}. "
                f"Marking event {event_id} processed."
            )
        elif item.stock_quantity < quantity:
            logger.warning(
                f"Insufficient stock for product {product_id}. "
                f"Available: {item.stock_quantity}, Required: {quantity}. "
                f"Marking event {event_id} processed."
            )
        else:
            # Deduct stock
            item.stock_quantity -= quantity
            logger.info(
                f"Stock updated for {product_id}: remaining stock is {item.stock_quantity} "
                f"(deducted {quantity} units for order {order_id})"
            )

        # Mark event as processed
        db.add(ProcessedEvent(event_id=event_id))
        db.commit()
        return True
    except Exception as exc:
        db.rollback()
        logger.error(f"Database error during event processing ({event_id}): {exc}")
        return False  # Will cause nack / retry
    finally:
        db.close()


async def start_inventory_consumer(rabbitmq_client: RabbitMQClient):
    """
    Background worker loop to listen for order-created events from RabbitMQ.
    """
    await rabbitmq_client.consume(
        queue_name=settings.RABBITMQ_ORDER_CREATED_QUEUE,
        routing_key="order.created",
        callback=handle_order_created_event
    )
