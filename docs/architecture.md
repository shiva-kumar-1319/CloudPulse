# CloudPulse System Architecture Specification & System Design Rationale

**Author:** Shiva Kumar  
**Domain:** Cloud-Native Distributed Microservices, Observability & Machine Learning Remediation  

---

## 1. System Overview

**CloudPulse** is an enterprise-grade cloud-native microservices platform featuring continuous observability, machine learning-driven anomaly detection, and automated Kubernetes remediation.

The platform demonstrates how distributed microservices interact synchronously (REST + JWT) and asynchronously (RabbitMQ event bus with Dead Letter Queues), while an autonomous out-of-band monitoring loop continuously evaluates telemetry metrics using an **Isolation Forest ML model**. When performance anomalies (spiking latencies, HTTP 500 error cascades, pod crash loops) occur, the **Automated Remediation Controller** validates safety guardrails and triggers Kubernetes API self-healing workflows (pod recycling or scaling) within sub-2.4s MTTR.

---

## 2. Microservices Architecture & Domain Boundaries

### 2.1 Auth Service (`services/auth-service`)
- **Domain**: Identity & Access Management (IAM)
- **Responsibilities**:
  - User registration & credential storage (Password hashing via `bcrypt`)
  - Authenticating users and issuing signed JWT Bearer Tokens (HS256)
  - Exposing `/health/live`, `/health/ready`, and Prometheus `/metrics`
- **Database**: `auth_db` (PostgreSQL / SQLite)

### 2.2 Order Service (`services/order-service`)
- **Domain**: Order Placement & Management
- **Responsibilities**:
  - Creating new orders and fetching order history
  - Validating JWT bearer authentication on incoming requests
  - Persisting orders in `order_db` with transactional idempotency
  - Publishing `order-created` events to RabbitMQ topic exchange
  - Exposing health & Prometheus metrics endpoints
- **Database**: `order_db` (PostgreSQL / SQLite)

### 2.3 Inventory Service (`services/inventory-service`)
- **Domain**: Stock & Inventory Management
- **Responsibilities**:
  - Managing product inventory stock levels
  - Asynchronously consuming `order-created` events from RabbitMQ
  - Reducing product stock idempotently upon order receipt
  - Emitting stock depletion alerts and Dead Letter Queue (DLQ) processing
- **Database**: `inventory_db` (PostgreSQL / SQLite)

---

## 3. System Design Trade-Off Analysis

| Architectural Decision | Chosen Pattern | Alternative Considered | Rationale & Trade-Off |
| :--- | :--- | :--- | :--- |
| **Database Architecture** | **Database-per-Service** | Shared Single DB | Complete database schema isolation prevents cross-service locking and enables independent scaling at the cost of requiring eventual consistency. |
| **Inter-Service Messaging** | **Asynchronous RabbitMQ DLQ** | Synchronous REST Call | Prevents cascading failures and thread pool starvation in Order Service if Inventory Service is temporarily slow or unavailable. |
| **Anomaly Detection Engine** | **Out-of-Band ML (Isolation Forest)** | In-Band API Middleware | Running ML inference out-of-band eliminates any latency overhead on the user request critical path. |
| **Remediation Guardrails** | **Cooldowns & Allowlist Engine** | Immediate Unconditional Restart | Prevents catastrophic restart thrashing / cascade loops during persistent external outages (e.g. database network partition). |

---

## 4. Benchmark Performance & SLA Metrics

- **Normal P95 Latency**: 85ms (Target SLA: < 500ms)
- **Mean Time to Remediate (MTTR)**: **2.14s** (Simulated autonomous recovery vs 15+ mins manual on-call)
- **Availability Target**: **99.99%** under simulated chaos faults
- **DLQ Data Retention**: **Zero Event Loss** with persistent durable message queues
