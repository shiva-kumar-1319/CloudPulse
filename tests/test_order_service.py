import os
import pytest
from fastapi.testclient import TestClient

os.environ["ORDER_DB_URL"] = "sqlite:///./test_order.db"

from services.order_service.app.main import app
from services.order_service.app.database import Base, engine
from shared.auth import create_access_token

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def auth_header():
    token = create_access_token({"sub": "user_123456", "username": "order_tester"})
    return {"Authorization": f"Bearer {token}"}


def test_order_health_endpoints():
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_and_get_order(auth_header):
    payload = {
        "product_id": "P1001",
        "quantity": 3
    }
    # Create Order
    response_create = client.post("/orders", json=payload, headers=auth_header)
    assert response_create.status_code == 201
    data = response_create.json()
    assert data["product_id"] == "P1001"
    assert data["quantity"] == 3
    assert data["user_id"] == "user_123456"
    assert data["status"] == "PENDING"

    order_id = data["id"]

    # Fetch Order
    response_get = client.get(f"/orders/{order_id}", headers=auth_header)
    assert response_get.status_code == 200
    assert response_get.json()["id"] == order_id

    # List Orders
    response_list = client.get("/orders", headers=auth_header)
    assert response_list.status_code == 200
    assert len(response_list.json()) == 1


def test_unauthenticated_order_creation():
    response = client.post("/orders", json={"product_id": "P1001", "quantity": 1})
    assert response.status_code == 403 or response.status_code == 401
