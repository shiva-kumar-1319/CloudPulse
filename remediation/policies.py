import time
from typing import Dict, List, Tuple, Any
from shared.logging import get_logger

logger = get_logger("remediation-policy")


class RemediationPolicyEngine:
    """
    Evaluates safety guardrails before executing automated self-healing actions.
    Prevents restart loops, unauthorized workload targets, and low-confidence triggers.
    Includes exponential backoff and active cooldown state inspection.
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
        # Track consecutive remediation count for exponential backoff
        self.consecutive_remediations: Dict[str, int] = {}

    def get_effective_cooldown(self, service_name: str) -> int:
        """
        Calculate effective cooldown duration applying exponential backoff if repeated.
        """
        consecutive = self.consecutive_remediations.get(service_name, 0)
        multiplier = min(4, 2 ** max(0, consecutive - 1)) if consecutive > 1 else 1
        return self.cooldown_seconds * multiplier

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

        # Check 3: Effective Cooldown Timer with Exponential Backoff
        effective_cooldown = self.get_effective_cooldown(service_name)
        last_time = self.last_remediation_time.get(service_name, 0.0)
        elapsed = now - last_time
        if elapsed < effective_cooldown:
            remaining = int(effective_cooldown - elapsed)
            return False, f"Service '{service_name}' is in remediation cooldown ({remaining}s remaining, effective: {effective_cooldown}s)"

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
        Record timestamp and increment remediation history.
        """
        now = time.time()
        self.last_remediation_time[service_name] = now
        if service_name not in self.remediation_history:
            self.remediation_history[service_name] = []
        self.remediation_history[service_name].append(now)
        self.consecutive_remediations[service_name] = self.consecutive_remediations.get(service_name, 0) + 1

    def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """
        Return comprehensive guardrail policy status for target workload.
        """
        now = time.time()
        last_time = self.last_remediation_time.get(service_name, 0.0)
        effective_cd = self.get_effective_cooldown(service_name)
        elapsed = now - last_time
        in_cooldown = elapsed < effective_cd if last_time > 0 else False
        remaining = int(effective_cd - elapsed) if in_cooldown else 0

        return {
            "service_name": service_name,
            "in_allowlist": service_name in self.allowlist,
            "in_cooldown": in_cooldown,
            "cooldown_remaining_seconds": remaining,
            "hourly_attempts": len([t for t in self.remediation_history.get(service_name, []) if (now - t) < 3600]),
            "max_hourly_allowed": self.max_attempts_per_hour,
            "consecutive_count": self.consecutive_remediations.get(service_name, 0)
        }
