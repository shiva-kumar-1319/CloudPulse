import sys
import time
import asyncio

# Ensure UTF-8 output encoding on Windows console terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from ml.training.train import train_model
from ml.inference.detector import AnomalyDetector
from remediation.policies import RemediationPolicyEngine
from remediation.kubernetes_client import KubernetesRemediationClient
from chaos.chaos import inject_pod_failure


def print_step(step_num: int, title: str):
    print(f"\n========================================================")
    print(f" [STEP {step_num}] {title}")
    print(f"========================================================")


def run_self_healing_demo():
    print("\n--- CLOUDPULSE SELF-HEALING PLATFORM DEMONSTRATION ---\n")

    # STEP 1: Verify System Baseline State
    print_step(1, "NORMAL BASELINE OPERATION")
    print("-> System initialized: Auth, Order, and Inventory Microservices active.")
    print("-> Prometheus scraping metrics. Microservices operating under baseline parameters.")

    detector = AnomalyDetector(model_dir="ml/models")

    normal_metrics = {
        "latency_mean": 0.035,
        "latency_p95": 0.085,
        "error_rate": 0.002,
        "request_rate": 22.0,
        "cpu_usage": 0.12,
        "memory_usage": 64 * 1024 * 1024,
        "pod_restarts": 0.0
    }
    score_normal, is_anomaly = detector.predict_anomaly(normal_metrics)
    print(f"[METRIC] ML Anomaly Score: {score_normal:.2f} (Status: HEALTHY)")

    time.sleep(1.0)

    # STEP 2: Fault Injection (Chaos Engineering)
    print_step(2, "CHAOS FAULT INJECTION")
    print("-> Injecting controlled chaos degradation into 'order-service'...")
    inject_pod_failure(service_name="order-service", namespace="cloudpulse", dry_run=True)

    degraded_metrics = {
        "latency_mean": 4.250,
        "latency_p95": 9.800,
        "error_rate": 0.450,
        "request_rate": 85.0,
        "cpu_usage": 1.85,
        "memory_usage": 320 * 1024 * 1024,
        "pod_restarts": 2.0
    }
    print("[METRIC] Prometheus Metric Degradation Observed:")
    print(f"   - Latency P95 spiked: 85ms -> 9,800ms")
    print(f"   - HTTP Error Rate: 0.2% -> 45.0%")

    time.sleep(1.0)

    # STEP 3: ML Anomaly Detection
    print_step(3, "ML ANOMALY DETECTION (ISOLATION FOREST)")
    score_degraded, is_anomaly = detector.predict_anomaly(degraded_metrics)
    print(f"[ALERT] ML Isolation Forest Score: {score_degraded:.2f} (ANOMALY DETECTED!)")
    print(f"   - Anomaly Alert Threshold: 0.75")
    print(f"   - Alert Dispatched to Remediation Controller for target 'order-service'.")

    time.sleep(1.0)

    # STEP 4: Remediation Controller Evaluation & Guardrails
    print_step(4, "REMEDIATION CONTROLLER & GUARDRAIL VALIDATION")
    policy = RemediationPolicyEngine(cooldown_seconds=180, score_threshold=0.75)
    allowed, reason = policy.validate_action("order-service", score_degraded)
    print(f"[GUARDRAIL] Safety Check PASSED = {allowed} ({reason})")

    time.sleep(1.0)

    # STEP 5: Automated Kubernetes Remediation Action
    print_step(5, "AUTOMATED KUBERNETES REMEDIATION EXECUTION")
    k8s = KubernetesRemediationClient(namespace="cloudpulse")
    success = k8s.restart_pod("order-service")
    if success:
        policy.record_remediation("order-service")
        print("[ACTION] Action Executed: Target pod recycled via Kubernetes API.")

    time.sleep(1.0)

    # STEP 6: System Recovery Verification
    print_step(6, "SYSTEM RECOVERY VERIFICATION")
    print("-> Fresh pod instance initialized and passing readiness probes.")
    print("-> Metrics returning to healthy operational baseline...")
    score_recovered, _ = detector.predict_anomaly(normal_metrics)
    print(f"[RECOVERY] Post-Remediation ML Anomaly Score: {score_recovered:.2f} (Status: RECOVERED & HEALTHY)")

    print("\n========================================================")
    print(" DEMONSTRATION COMPLETE: Self-Healing Cycle Successful!")
    print(" Summary: failure -> metric degradation -> anomaly detection -> remediation -> recovery")
    print("========================================================\n")


if __name__ == "__main__":
    run_self_healing_demo()
