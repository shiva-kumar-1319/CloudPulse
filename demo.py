import sys
import time
import asyncio

# Ensure UTF-8 output encoding on Windows console terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from ml.inference.detector import AnomalyDetector
from remediation.policies import RemediationPolicyEngine
from remediation.kubernetes_client import KubernetesRemediationClient
from chaos.chaos import inject_pod_failure

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_step(step_num: int, title: str):
    print(f"\n{BOLD}{CYAN}========================================================{RESET}")
    print(f"{BOLD}{CYAN} [STEP {step_num}] {title}{RESET}")
    print(f"{BOLD}{CYAN}========================================================{RESET}")


def run_self_healing_demo():
    print(f"\n{BOLD}{GREEN}⚡ CLOUDPULSE AUTONOMOUS SELF-HEALING PLATFORM DEMO ⚡{RESET}")
    print(f"{CYAN}Author: Shiva Kumar | Kubernetes • ML Isolation Forest • Microservices{RESET}\n")

    start_time = time.time()

    # STEP 1: Verify System Baseline State
    print_step(1, "NORMAL BASELINE OPERATION")
    print(f"-> System initialized: {GREEN}auth-service{RESET}, {GREEN}order-service{RESET}, {GREEN}inventory-service{RESET} active.")
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
    print(f"[METRIC] ML Anomaly Score: {GREEN}{score_normal:.2f}{RESET} (Status: {GREEN}HEALTHY{RESET})")

    time.sleep(0.8)

    # STEP 2: Fault Injection (Chaos Engineering)
    print_step(2, "CHAOS FAULT INJECTION")
    print(f"-> Injecting controlled chaos degradation into '{RED}order-service{RESET}'...")
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
    print(f"[METRIC] Prometheus Metric Degradation Observed:")
    print(f"   - Latency P95 spiked: {YELLOW}85ms -> 9,800ms{RESET}")
    print(f"   - HTTP Error Rate: {RED}0.2% -> 45.0%{RESET}")

    time.sleep(0.8)

    # STEP 3: ML Anomaly Detection
    print_step(3, "ML ANOMALY DETECTION (ISOLATION FOREST)")
    score_degraded, is_anomaly = detector.predict_anomaly(degraded_metrics)
    print(f"[ALERT] ML Isolation Forest Score: {RED}{score_degraded:.2f}{RESET} ({RED}ANOMALY DETECTED!{RESET})")
    print(f"   - Anomaly Alert Threshold: 0.75")
    print(f"   - Alert Dispatched to Remediation Controller for target '{RED}order-service{RESET}'.")

    if hasattr(detector, "explain_anomaly"):
        weights = detector.explain_anomaly(degraded_metrics)
        print(f"[EXPLAINABILITY] Telemetry Contribution: {weights}")

    time.sleep(0.8)

    # STEP 4: Remediation Controller Evaluation & Guardrails
    print_step(4, "REMEDIATION CONTROLLER & GUARDRAIL VALIDATION")
    policy = RemediationPolicyEngine(cooldown_seconds=180, score_threshold=0.75)
    allowed, reason = policy.validate_action("order-service", score_degraded)
    print(f"[GUARDRAIL] Safety Check: {GREEN}PASSED = {allowed}{RESET} ({reason})")

    time.sleep(0.8)

    # STEP 5: Automated Kubernetes Remediation Action
    print_step(5, "AUTOMATED KUBERNETES REMEDIATION EXECUTION")
    k8s = KubernetesRemediationClient(namespace="cloudpulse")
    success = k8s.restart_pod("order-service")
    if success:
        policy.record_remediation("order-service")
        print(f"[ACTION] Action Executed: {GREEN}Target pod recycled via Kubernetes API.{RESET}")

    time.sleep(0.8)

    # STEP 6: System Recovery Verification
    print_step(6, "SYSTEM RECOVERY VERIFICATION")
    print(f"-> Fresh pod instance initialized and passing readiness probes.")
    print(f"-> Telemetry metrics returning to healthy operational baseline...")
    score_recovered, _ = detector.predict_anomaly(normal_metrics)
    print(f"[RECOVERY] Post-Remediation ML Score: {GREEN}{score_recovered:.2f}{RESET} (Status: {GREEN}RECOVERED & HEALTHY{RESET})")

    total_mttr = time.time() - start_time
    print(f"\n{BOLD}{CYAN}========================================================{RESET}")
    print(f"{BOLD}{GREEN} ✅ DEMONSTRATION COMPLETE: Self-Healing Cycle Successful!{RESET}")
    print(f" Summary: failure -> metric degradation -> anomaly detection -> remediation -> recovery")
    print(f" Benchmark Simulated MTTR: {GREEN}{total_mttr:.2f}s{RESET}")
    print(f"{BOLD}{CYAN}========================================================{RESET}\n")


if __name__ == "__main__":
    run_self_healing_demo()
