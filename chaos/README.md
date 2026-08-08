# CloudPulse Chaos Engineering Toolkit

The Chaos Engineering toolkit enables controlled fault injection to test and validate CloudPulse's automated self-healing loop:

```text
[ Chaos Fault Injection ] ──> [ Prometheus Metrics Spike ] ──> [ ML Anomaly Detection ] ──> [ Remediation Controller ] ──> [ K8s Recovery ]
```

---

## ⚡ Usage Examples

### 1. Pod Termination (Simulate Crashed / Unhealthy Container)
```bash
python chaos/chaos.py --kill-pod order-service --namespace cloudpulse
```

### 2. Latency Injection (Simulate Slow Database / Network Degradation)
```bash
python chaos/chaos.py --latency order-service --seconds 3.5
```

### 3. Error Rate Injection (Simulate Internal Server Failures)
```bash
python chaos/chaos.py --errors inventory-service --rate 0.50
```

### 4. Dry Run Mode (Safety Check)
```bash
python chaos/chaos.py --kill-pod auth-service --dry-run
```

---

## 🛡️ Chaos Safeguards
1. **Namespace Restriction**: Restricted to `cloudpulse` namespace.
2. **Service Allowlist**: Operates strictly against `auth-service`, `order-service`, and `inventory-service`.
3. **Dry Run Option**: Enables dry-run validation prior to execution.
