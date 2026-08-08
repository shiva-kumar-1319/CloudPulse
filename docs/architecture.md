# CloudPulse System Architecture Specification

## 1. System Overview

CloudPulse is a cloud-native microservices platform featuring continuous observability, machine learning-driven anomaly detection, and automated Kubernetes remediation.

The platform demonstrates how microservices interact synchronously (REST + JWT) and asynchronously (RabbitMQ event bus), while an out-of-band monitoring loop continuously checks system metrics and triggers self-healing interventions when degrading behaviors (latencies, errors, pod restarts) are detected.

---

## 2. Service Responsibilities & Domain Boundaries

### 2.1 Auth Service (`services/auth-service`)
- **Domain**: Identity & Access Management (IAM)
- **Responsibilities**:
  - User registration & credential management (Password hashing via `bcrypt`)
  - Authenticating users and issuing JWT Bearer Tokens (HS256)
  - JWT token verification public endpoint / utility module
  - Exposing `/health/live`, `/health/ready`, and Prometheus `/metrics`
- **Database**: `auth_db` (PostgreSQL / SQLite for local unit test)

### 2.2 Order Service (`services/order-service`)
- **Domain**: Order Management
- **Responsibilities**:
  - Creating new orders and fetching order details
  - Validating JWT bearer authentication on incoming requests
  - Persisting orders in `order_db` with `PENDING` status
  - Publishing `order-created` event to RabbitMQ topic exchange
  - Exposing health & Prometheus metrics endpoints
- **Database**: `order_db` (PostgreSQL / SQLite for local unit test)

### 2.3 Inventory Service (`services/inventory-service`)
- **Domain**: Stock & Inventory Management
- **Responsibilities**:
  - Managing product inventory stock levels
  - Asynchronously consuming `order-created` events from RabbitMQ
  - Reducing product stock idempotently upon order receipt
  - Emitting stock depletion warnings or order status updates
  - Exposing REST APIs for stock lookup, stock update, health & metrics
- **Database**: `inventory_db` (PostgreSQL / SQLite for local unit test)

---

## 3. Database-per-Service Architecture

Strict domain isolation is maintained across all services:
- **No Shared Databases**: No service accesses another service's database.
- **Data Consistency**: Eventual consistency achieved via RabbitMQ events.
- **Local Dev / Unit Testing**: SQLite file/in-memory databases supported for lightweight test suites.
- **Container / Production**: PostgreSQL instances per service.

---

## 4. Communication Protocols & Event Schema

### 4.1 Synchronous Communication (REST)
- **Format**: JSON payloads over HTTP/1.1
- **API Spec**: OpenAPI 3.0 via FastAPI `/docs`
- **Authentication**: `Authorization: Bearer <JWT_TOKEN>`

### 4.2 Asynchronous Event Bus (RabbitMQ)
- **Exchange**: `cloudpulse.events` (Topic Exchange)
- **Routing Key**: `order.created`
- **Queue**: `inventory.order-created.queue`
- **Dead Letter Exchange (DLX)**: `cloudpulse.dlx` with queue `inventory.order-created.dlq`
- **Delivery**: Persistent messages (durable queue + delivery mode 2) with explicit manual acknowledgements (`ack`).

#### `order-created` Event Payload Schema:
```json
{
  "event_id": "evt_9f8a3c1e-4b2a-4c8d-8a1e-5f9a2b3c4d5e",
  "event_type": "order-created",
  "timestamp": "2026-08-08T09:45:00Z",
  "order_id": "ord_12345678-aaaa-bbbb-cccc-ddddeeeeffff",
  "user_id": "usr_87654321-ffff-eeee-dddd-ccccbbbbaaaa",
  "product_id": "prod_P1001",
  "quantity": 2
}
```

---

## 5. Observability Strategy

Every microservice exposes standardized Prometheus metrics at `GET /metrics`:
- `http_requests_total{service="...", method="...", endpoint="...", status_code="..."}`
- `http_request_duration_seconds{service="...", endpoint="..."}`
- `http_requests_errors_total{service="...", error_type="..."}`
- Standard Python runtime metrics (`process_cpu_seconds_total`, `process_resident_memory_bytes`).

Prometheus scrapes targets every 5 seconds in local/Minikube setups to ensure high resolution for anomaly detection.

---

## 6. ML Anomaly Detection & Self-Healing Remediation

```text
[ Microservices Prometheus Metrics ]
              │
              ▼
   [ Prometheus Scraper ]
              │
              ▼
[ Ingestion & Feature Engineering ]
(Calculates latency_p95, error_rate, cpu, memory, restarts)
              │
              ▼
  [ ML Model: Isolation Forest ]
(Evaluates feature vector -> Anomaly Score)
              │
              ▼ (Score > Threshold & Guardrails Pass)
  [ Remediation Controller ]
              │
              ▼
 [ Kubernetes API (Restart Pod / Scale Deployment) ]
```

### 6.1 Anomaly Detector (Isolation Forest)
- **Features**: `latency_mean`, `latency_p95`, `error_rate`, `request_rate`, `cpu_usage`, `memory_usage`, `pod_restarts`.
- **Reasoning for Isolation Forest**: Unsupervised, lightweight, fast evaluation, low resource overhead, does not require massive failure datasets.

### 6.2 Remediation Safeguards
- **Score Thresholding**: Only scores indicating high contamination trigger action.
- **Cooldown Period**: Minimum 180s delay between remediation actions on the same service to prevent restart loops.
- **Workload Allowlist**: Only explicit services (`order-service`, `inventory-service`, `auth-service`) are remediable.
- **Max Attempt Count**: Maximum 3 consecutive attempts per hour before alerting human operator.

---

## 7. Chaos Engineering & Safety Boundaries

- **Tool**: `chaos/chaos.py` CLI tool.
- **Capabilities**: Pod killing (`--kill-pod`), artificial response delay (`--latency`), simulated HTTP 500 errors (`--errors`).
- **Safety Features**:
  - Namespace restriction (`cloudpulse` namespace only).
  - Explicit confirmation or `--dry-run` flag requirement.
  - Hard disabled against non-dev clusters (checks K8s cluster context).

---

## 8. Deployment Strategy & Cost Boundaries

| Component | Local Development | Minikube (K8s Local) | Cloud Production (AWS) | Cost Implications |
|-----------|-------------------|----------------------|-----------------------|-------------------|
| Services | FastAPI (Uvicorn) | Pods in Minikube | Pods on EKS Node Group | Local: $0 / Cloud: EKS compute |
| Database | SQLite / Postgres Compose | StatefulSets / Helm Postgres | AWS RDS PostgreSQL | Local: $0 / Cloud: RDS cost |
| Event Bus | Docker RabbitMQ | Containerized RabbitMQ | Managed / Containerized RabbitMQ | Local: $0 / Cloud: Compute |
| Monitoring | Prometheus & Grafana Containers | Prometheus Operator / Deployment | Managed Prometheus/Grafana or EKS | Local: $0 / Cloud: Compute/Storage |
| IaC | N/A | Helm / Manifests | Terraform | Local: $0 / Tool: Free |
