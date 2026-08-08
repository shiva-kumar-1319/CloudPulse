import os
import pytest
import asyncio
from fastapi.testclient import TestClient

os.environ["INVENTORY_DB_URL"] = "sqlite:///./test_inventory.db"

from services.inventory_service.app.main import app
from services.inventory_service.app.database import Base, engine, SessionLocal
from services.inventory_service.app.models import InventoryItem
from services.inventory_service.app.consumer import handle_order_created_event

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_inventory_api():
    # Seed product
    payload = {
        "product_id": "P1001",
        "product_name": "CloudPulse Gateway Router",
        "stock_quantity": 50
    }
    response_create = client.post("/inventory", json=payload)
    assert response_create.status_code == 201
    assert response_create.json()["stock_quantity"] == 50

    # Fetch stock
    response_get = client.get("/inventory/P1001")
    assert response_get.status_code == 200
    assert response_get.json()["stock_quantity"] == 50

    # Update stock
    response_patch = client.patch("/inventory/P1001", json={"stock_quantity": 100})
    assert response_patch.status_code == 200
    assert response_patch.json()["stock_quantity"] == 100


@pytest.mark.asyncio
async def test_order_created_event_consumer_deduction_and_idempotency():
    # Seed initial inventory stock directly
    db = SessionLocal()
    db.add(InventoryItem(product_id="P1002", product_name="CloudPulse Sensor Node", stock_quantity=20))
    db.commit()
    db.close()

    event_payload = {
        "event_id": "evt_test_001",
        "event_type": "order-created",
        "order_id": "ord_999",
        "user_id": "usr_111",
        "product_id": "P1002",
        "quantity": 5
    }

    # First event processing -> stock reduces 20 -> 15
    processed_1 = await handle_order_created_event(event_payload)
    assert processed_1 is True

    db = SessionLocal()
    item_1 = db.get(InventoryItem, "P1002")
    assert item_1.stock_quantity == 15
    db.close()

    # Second event processing with SAME event_id -> stock MUST remain 15 (Idempotency)
    processed_2 = await handle_order_created_event(event_payload)
    assert processed_2 is True

    db = SessionLocal()
    item_2 = db.get(InventoryItem, "P1002")
    assert item_2.stock_quantity == 15
    db.close()
