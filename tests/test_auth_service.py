import os
import pytest
from fastapi.testclient import TestClient

# Ensure SQLite test DB URL before importing app modules
os.environ["AUTH_DB_URL"] = "sqlite:///./test_auth.db"

from services.auth_service.app.main import app
from services.auth_service.app.database import Base, engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_auth_health_endpoints():
    response_live = client.get("/health/live")
    assert response_live.status_code == 200
    assert response_live.json()["status"] == "healthy"

    response_ready = client.get("/health/ready")
    assert response_ready.status_code == 200
    assert response_ready.json()["status"] == "healthy"


def test_user_registration_and_login():
    # Register user
    reg_payload = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "securepassword123"
    }
    response_reg = client.post("/auth/register", json=reg_payload)
    assert response_reg.status_code == 201
    data_reg = response_reg.json()
    assert data_reg["username"] == "testuser"
    assert "id" in data_reg
    assert "password" not in data_reg

    # Duplicate username check
    response_dup = client.post("/auth/register", json=reg_payload)
    assert response_dup.status_code == 400

    # Login user
    login_payload = {
        "username": "testuser",
        "password": "securepassword123"
    }
    response_login = client.post("/auth/login", json=login_payload)
    assert response_login.status_code == 200
    data_login = response_login.json()
    assert "access_token" in data_login
    assert data_login["token_type"] == "bearer"

    # Profile fetch with JWT
    token = data_login["access_token"]
    response_me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response_me.status_code == 200
    assert response_me.json()["username"] == "testuser"


def test_invalid_login():
    login_payload = {
        "username": "nonexistent",
        "password": "wrongpassword"
    }
    response = client.post("/auth/login", json=login_payload)
    assert response.status_code == 401
