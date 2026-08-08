import pytest
from chaos.chaos import inject_pod_failure, inject_service_latency, inject_service_errors


def test_chaos_safeguards():
    # Unauthorized namespace -> Blocked
    res_ns = inject_pod_failure("order-service", namespace="production-cluster", dry_run=False)
    assert res_ns is False

    # Unauthorized service -> Blocked
    res_svc = inject_pod_failure("kube-system-dns", namespace="cloudpulse", dry_run=False)
    assert res_svc is False


def test_chaos_dry_run():
    res_dry = inject_pod_failure("order-service", namespace="cloudpulse", dry_run=True)
    assert res_dry is True

    res_lat = inject_service_latency("order-service", seconds=2.0, dry_run=True)
    assert res_lat is True

    res_err = inject_service_errors("order-service", rate=0.40, dry_run=True)
    assert res_err is True
