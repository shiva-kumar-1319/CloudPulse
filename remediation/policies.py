import time
from typing import Dict, List, Tuple
from shared.logging import get_logger

logger = get_logger("remediation-policy")


class RemediationPolicyEngine:
    """
    Evaluates safety guardrails before executing automated self-healing actions.
    Prevents restart loops, unauthorized workload targets, and low-confidence triggers.
    """
    def __init__(
        self,
        allowlist: List[str] = None,
        score_threshold: float = 0.75,
        cooldown_seconds: int = 180,
        max_attempts_per_hour: int = 3
    ):
        self.allowlist = allowlist or ["auth-service", "order-service", "inventory-service"]
        self.score_threshold = score_threshold
        self.cooldown_seconds = cooldown_seconds
        self.max_attempts_per_hour = max_attempts_per_hour
        
        # Track last remediation timestamp per service
        self.last_remediation_time: Dict[str, float] = {}
        # Track hourly attempts history per service
        self.remediation_history: Dict[str, List[float]] = {}

    def validate_action(self, service_name: str, anomaly_score: float) -> Tuple[bool, str]:
        """
        Validate whether self-healing intervention is permitted for target service.
        Returns:
            allowed (bool): True if safety checks pass, False otherwise.
            reason (str): Explanation of decision.
        """
        now = time.time()

        # Check 1: Target Workload Allowlist
        if service_name not in self.allowlist:
            return False, f"Service '{service_name}' is not in remediation allowlist ({self.allowlist})"

        # Check 2: Anomaly Threshold Verification
        if anomaly_score < self.score_threshold:
            return False, f"Anomaly score ({anomaly_score:.2f}) is below threshold ({self.score_threshold:.2f})"

        # Check 3: Cooldown Timer
        last_time = self.last_remediation_time.get(service_name, 0.0)
        elapsed = now - last_time
        if elapsed < self.cooldown_seconds:
            remaining = int(self.cooldown_seconds - elapsed)
            return False, f"Service '{service_name}' is in remediation cooldown ({remaining}s remaining)"

        # Check 4: Hourly Rate Limiting
        history = self.remediation_history.get(service_name, [])
        # Prune attempts older than 1 hour (3600s)
        history = [t for t in history if (now - t) < 3600]
        self.remediation_history[service_name] = history

        if len(history) >= self.max_attempts_per_hour:
            return False, f"Maximum remediation attempts ({self.max_attempts_per_hour}/hr) exceeded for '{service_name}'"

        return True, "All remediation safety guardrails PASSED"

    def record_remediation(self, service_name: str):
        """
        Record timestamp of executed remediation action.
        """
        now = time.time()
        self.last_remediation_time[service_name] = now
        if service_name not in self.remediation_history:
            self.remediation_history[service_name] = []
        self.remediation_history[service_name].append(now)
