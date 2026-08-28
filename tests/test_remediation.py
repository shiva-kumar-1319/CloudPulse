import pytest
from fastapi.testclient import TestClient
from remediation.controller import app, policy_engine
from remediation.policies import RemediationPolicyEngine

client = TestClient(app)


def test_remediation_policy_guardrails():
    policy = RemediationPolicyEngine(cooldown_seconds=10, score_threshold=0.75)

    # 1. Below threshold -> Blocked
    allowed, reason = policy.validate_action("order-service", 0.50)
    assert allowed is False
    assert "below threshold" in reason

    # 2. Not in allowlist -> Blocked
    allowed, reason = policy.validate_action("unauthorized-db", 0.90)
    assert allowed is False
    assert "allowlist" in reason

    # 3. High anomaly score -> Allowed
    allowed, reason = policy.validate_action("order-service", 0.85)
    assert allowed is True

    # Record remediation execution
    policy.record_remediation("order-service")

    # 4. Immediate second attempt -> Blocked by Cooldown
    allowed_cooldown, reason_cooldown = policy.validate_action("order-service", 0.95)
    assert allowed_cooldown is False
    assert "cooldown" in reason_cooldown


def test_remediation_exponential_backoff_and_status():
    policy = RemediationPolicyEngine(cooldown_seconds=10, score_threshold=0.75)
    status_initial = policy.get_service_status("order-service")
    assert status_initial["in_allowlist"] is True
    assert status_initial["in_cooldown"] is False
    assert status_initial["consecutive_count"] == 0

    # Trigger first remediation
    policy.record_remediation("order-service")
    status_after = policy.get_service_status("order-service")
    assert status_after["in_cooldown"] is True
    assert status_after["consecutive_count"] == 1


def test_remediation_api_endpoint():
    # Reset policy state
    policy_engine.last_remediation_time.clear()

    payload = {
        "target_service": "inventory-service",
        "anomaly_score": 0.88,
        "recommended_action": "restart_pod"
    }
    response = client.post("/remediation/alert", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["target_service"] == "inventory-service"
    assert data["action_taken"] == "restart_pod"
