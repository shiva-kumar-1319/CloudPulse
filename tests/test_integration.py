import os
import pytest
from fastapi.testclient import TestClient

os.environ["AUTH_DB_URL"] = "sqlite:///./test_integ_auth.db"
os.environ["ORDER_DB_URL"] = "sqlite:///./test_integ_order.db"
os.environ["INVENTORY_DB_URL"] = "sqlite:///./test_integ_inventory.db"

from services.auth_service.app.main import app as auth_app
from services.auth_service.app.database import Base as AuthBase, engine as auth_engine
from services.order_service.app.main import app as order_app
from services.order_service.app.database import Base as OrderBase, engine as order_engine
from services.inventory_service.app.main import app as inventory_app
from services.inventory_service.app.database import Base as InvBase, engine as inv_engine
from services.inventory_service.app.consumer import handle_order_created_event

auth_client = TestClient(auth_app)
order_client = TestClient(order_app)
inventory_client = TestClient(inventory_app)


@pytest.fixture(autouse=True)
def setup_databases():
    AuthBase.metadata.create_all(bind=auth_engine)
    OrderBase.metadata.create_all(bind=order_engine)
    InvBase.metadata.create_all(bind=inv_engine)
    yield
    AuthBase.metadata.drop_all(bind=auth_engine)
    OrderBase.metadata.drop_all(bind=order_engine)
    InvBase.metadata.drop_all(bind=inv_engine)


@pytest.mark.asyncio
async def test_full_cloudpulse_e2e_flow():
    # 1. Register User in Auth Service
    reg_resp = auth_client.post("/auth/register", json={
        "username": "alice",
        "email": "alice@cloudpulse.io",
        "password": "securepassword123"
    })
    assert reg_resp.status_code == 201

    # 2. Login User to obtain JWT token
    login_resp = auth_client.post("/auth/login", json={
        "username": "alice",
        "password": "securepassword123"
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Seed Inventory in Inventory Service
    inv_resp = inventory_client.post("/inventory", json={
        "product_id": "P5000",
        "product_name": "CloudPulse Edge Node",
        "stock_quantity": 100
    })
    assert inv_resp.status_code == 201
    assert inv_resp.json()["stock_quantity"] == 100

    # 4. Create Order in Order Service using JWT Bearer auth
    order_resp = order_client.post("/orders", json={
        "product_id": "P5000",
        "quantity": 10
    }, headers=headers)
    assert order_resp.status_code == 201
    order_data = order_resp.json()
    assert order_data["status"] == "PENDING"
    order_id = order_data["id"]

    # 5. Simulate asynchronous event consumption by Inventory Service
    event_payload = {
        "event_id": f"evt_{order_id}",
        "event_type": "order-created",
        "order_id": order_id,
        "user_id": order_data["user_id"],
        "product_id": "P5000",
        "quantity": 10
    }
    processed = await handle_order_created_event(event_payload)
    assert processed is True

    # 6. Verify inventory stock reduced from 100 -> 90
    check_inv = inventory_client.get("/inventory/P5000")
    assert check_inv.status_code == 200
    assert check_inv.json()["stock_quantity"] == 90
