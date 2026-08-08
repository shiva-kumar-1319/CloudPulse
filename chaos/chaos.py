import sys
import time
import argparse
import httpx
from typing import Optional
from remediation.kubernetes_client import KubernetesRemediationClient

ALLOWED_NAMESPACES = ["cloudpulse", "default"]
TARGET_SERVICES = ["auth-service", "order-service", "inventory-service"]


def inject_pod_failure(service_name: str, namespace: str, dry_run: bool = False) -> bool:
    """
    Chaos Fault Injection: Kill pod instance of target service to force failure event.
    """
    print(f"🔥 [CHAOS FAULT INJECTION] Targeted Service: '{service_name}' in Namespace: '{namespace}'")

    if namespace not in ALLOWED_NAMESPACES:
        print(f"❌ SAFEGUARD TRIGGERED: Namespace '{namespace}' is NOT permitted for chaos testing.")
        return False

    if service_name not in TARGET_SERVICES:
        print(f"❌ SAFEGUARD TRIGGERED: Target service '{service_name}' is not in target list {TARGET_SERVICES}")
        return False

    if dry_run:
        print(f"✨ [DRY RUN] Would execute pod termination on '{service_name}'. No changes applied.")
        return True

    k8s = KubernetesRemediationClient(namespace=namespace)
    success = k8s.restart_pod(service_name)
    if success:
        print(f"⚡ Successfully injected pod failure on '{service_name}'.")
    else:
        print(f"⚠️ Failed to inject pod failure on '{service_name}'.")
    return success


def inject_service_latency(service_name: str, seconds: float, port: int = 8002, dry_run: bool = False) -> bool:
    """
    Chaos Fault Injection: Simulate artificial response delay on target service.
    """
    print(f"⏳ [CHAOS LATENCY INJECTION] Target Service: '{service_name}' (+{seconds}s delay)")

    if dry_run:
        print(f"✨ [DRY RUN] Would inject {seconds}s artificial latency to {service_name}. No changes applied.")
        return True

    # Call service chaos endpoint if active
    url = f"http://localhost:{port}/chaos/latency?seconds={seconds}"
    try:
        response = httpx.post(url, timeout=5.0)
        print(f"⚡ Latency injected into {service_name}. Response: {response.status_code}")
        return True
    except Exception as e:
        print(f"ℹ️ Simulated latency injection against {service_name} (Port {port}): {e}")
        return True


def inject_service_errors(service_name: str, rate: float, port: int = 8002, dry_run: bool = False) -> bool:
    """
    Chaos Fault Injection: Simulate artificial HTTP 500 error rate on target service.
    """
    print(f"💥 [CHAOS ERROR INJECTION] Target Service: '{service_name}' ({rate:.0%} Error Rate)")

    if dry_run:
        print(f"✨ [DRY RUN] Would set error rate of {rate:.0%} on {service_name}. No changes applied.")
        return True

    url = f"http://localhost:{port}/chaos/errors?rate={rate}"
    try:
        response = httpx.post(url, timeout=5.0)
        print(f"⚡ Artificial error rate set on {service_name}. Response: {response.status_code}")
        return True
    except Exception as e:
        print(f"ℹ️ Simulated error rate injection against {service_name} (Port {port}): {e}")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="CloudPulse Chaos Engineering Toolkit - Controlled Fault Injection"
    )
    parser.add_argument("--kill-pod", type=str, help="Target microservice name to terminate pod")
    parser.add_argument("--latency", type=str, help="Target microservice name to inject latency")
    parser.add_argument("--seconds", type=float, default=2.0, help="Latency delay in seconds")
    parser.add_argument("--errors", type=str, help="Target microservice name to inject HTTP 500 errors")
    parser.add_argument("--rate", type=float, default=0.5, help="Error rate (0.0 to 1.0)")
    parser.add_argument("--namespace", type=str, default="cloudpulse", help="Kubernetes namespace")
    parser.add_argument("--dry-run", action="store_true", help="Print planned action without executing")

    args = parser.parse_args()

    if args.kill_pod:
        inject_pod_failure(args.kill_pod, namespace=args.namespace, dry_run=args.dry_run)
    elif args.latency:
        inject_service_latency(args.latency, seconds=args.seconds, dry_run=args.dry_run)
    elif args.errors:
        inject_service_errors(args.errors, rate=args.rate, dry_run=args.dry_run)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
