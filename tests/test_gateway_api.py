import pytest
from fastapi.testclient import TestClient
from services.api_gateway.app.main import app

client = TestClient(app)


def test_gateway_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_dashboard_summary_endpoint():
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert "operational_mode" in data
    assert "system_status" in data
    assert data["healthy_services_count"] == 3


def test_services_health_cards_endpoint():
    response = client.get("/api/services")
    assert response.status_code == 200
    cards = response.json()
    assert len(cards) == 3
    service_names = [c["service_name"] for c in cards]
    assert "auth-service" in service_names
    assert "order-service" in service_names
    assert "inventory-service" in service_names


def test_chaos_pod_kill_endpoint():
    payload = {
        "target_service": "order-service",
        "namespace": "cloudpulse",
        "dry_run": True
    }
    response = client.post("/api/chaos/pod", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "executed"
    assert data["target_service"] == "order-service"

    # Verify event logged
    events_resp = client.get("/api/events")
    assert events_resp.status_code == 200
    assert len(events_resp.json()) > 0
