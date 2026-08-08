# CloudPulse — Production-Ready Self-Healing Cloud-Native Microservices Platform

[![CloudPulse Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](VERSION)
[![Architecture](https://img.shields.io/badge/architecture-Microservices-orange.svg)](#3-architecture)
[![Python](https://img.shields.io/badge/python-3.12%2B-green.svg)](https://www.python.org/)

---

## 1. Project Overview
**CloudPulse** is an enterprise-grade self-healing microservices platform. It demonstrates how distributed microservices interact via REST and asynchronous message queues while an autonomous out-of-band monitoring loop continuously evaluates telemetry metrics using an **Isolation Forest ML model**. When service degradation (spiking latencies, HTTP 500 error rates, pod restarts) is detected, the platform's **Automated Remediation Controller** validates safety guardrails and issues Kubernetes API calls (pod recycling or scaling) to restore healthy operational baselines.

---

## 2. Why This Project Exists
Modern cloud-native environments demand high availability and resilience. Traditional static alert rules fail to detect subtle, non-linear performance anomalies or require manual SRE intervention to recover. CloudPulse demonstrates:
- Microservices decoupling with Database-per-Service architecture.
- Asynchronous event-driven communication via RabbitMQ with idempotency & DLQ patterns.
- Real-time ML-driven anomaly detection on Prometheus time-series metrics.
- Closed-loop Kubernetes automated remediation guarded by rate limits and cooldown policies.
- Controlled chaos engineering for reliability testing.

---

## 3. Architecture

```mermaid
flowchart TD
    Client[Client / User] -->|REST / JWT| Auth[Auth Service]
    Client -->|REST / JWT| Order[Order Service]
    
    Order -->|Publish order-created| RabbitMQ[(RabbitMQ Event Bus)]
    RabbitMQ -->|Consume event| Inventory[Inventory Service]
    
    Auth --- AuthDB[(Auth DB)]
    Order --- OrderDB[(Order DB)]
    Inventory --- InventoryDB[(Inventory DB)]
    
    Auth -->|Metrics Scraping /metrics| Prometheus[Prometheus]
    Order -->|Metrics Scraping /metrics| Prometheus
    Inventory -->|Metrics Scraping /metrics| Prometheus
    
    Prometheus --> Ingest[Metrics Ingestion Pipeline]
    Ingest --> MLModel[ML Anomaly Detector\n(Isolation Forest)]
    MLModel -->|Anomaly Score > 0.75| Remediation[Remediation Controller]
    
    Remediation -->|Restart Pod / Scale| K8sAPI[Kubernetes API]
    
    Chaos[Chaos Testing Tool] -.->|Inject Failure| Order
    Chaos -.->|Pod Termination| K8sAPI

    Prometheus --> Grafana[Grafana Dashboards]
    Remediation -->|Remediation Metrics| Grafana
```

---

## 4. Repository Structure

```text
cloudpulse/
│
├── services/                  # Microservices Architecture
│   ├── auth_service/          # Authentication & JWT identity provider
│   ├── order_service/         # Order creation & REST API service
│   └── inventory_service/     # Inventory stock & RabbitMQ consumer service
│
├── shared/                    # Shared Core Python Libraries
│   ├── schemas/               # Common Pydantic v2 schemas & event contracts
│   ├── messaging/             # Async RabbitMQ client wrappers
│   ├── auth/                  # JWT handler & bcrypt password hashing
│   ├── logging/               # Structured JSON logger & Prometheus middleware
│   └── config/                # Environment configuration loader
│
├── ml/                        # Machine Learning Anomaly Detection Engine
│   ├── data/                  # Training metrics dataset
│   ├── ingestion/             # Prometheus metric ingestion client
│   ├── training/              # Isolation Forest model training script
│   ├── inference/             # Real-time anomaly detector & exporter service
│   └── models/                # Serialized model (.pkl) & metadata
│
├── remediation/               # Automated Kubernetes Remediation Controller
│   ├── controller.py          # Remediation alert API server & decision engine
│   ├── kubernetes_client.py   # RBAC-scoped Kubernetes API client
│   └── policies.py            # Cooldown timers, allowlist, rate limits
│
├── chaos/                     # Chaos Engineering Toolkit
│   ├── chaos.py               # Fault injection CLI tool
│   └── README.md              # Chaos testing manual
│
├── k8s/                       # Kubernetes Manifests
│   ├── namespace.yaml
│   ├── configmaps/
│   ├── secrets/
│   ├── auth_service/
│   ├── order_service/
│   ├── inventory_service/
│   ├── rabbitmq/
│   ├── postgres/
│   ├── prometheus/
│   ├── grafana/
│   ├── hpa/
│   └── rbac.yaml
│
├── terraform/                 # Infrastructure as Code (AWS EKS)
│   ├── modules/               # VPC & EKS modules
│   ├── main.tf
│   └── README.md              # Cloud Cost Warning & deployment guide
│
├── monitoring/                # Prometheus & Grafana Configuration
│   ├── prometheus/            # Scrape configuration
│   └── grafana/               # Pre-provisioned dashboards & datasources
│
├── .github/                   # CI/CD Workflows
│   └── workflows/             # GitHub Actions for test, build, deploy
│
├── tests/                     # Cross-service unit & integration tests
├── docker-compose.yml         # Local Docker Compose stack
├── Makefile                   # Developer automation targets
├── demo.py                    # End-to-end self-healing demonstration
├── .env.example               # Environment variables template
├── VERSION                    # Version tracking file
└── README.md                  # Main documentation page
```

---

## 5. Technology Stack
- **Core Languages & Frameworks**: Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2.x
- **Databases & Messaging**: PostgreSQL, SQLite (testing), RabbitMQ 3.13
- **Observability**: Prometheus, Grafana
- **Machine Learning**: scikit-learn (Isolation Forest), pandas, numpy, joblib
- **Containerization & Orchestration**: Docker, Docker Compose, Kubernetes, Minikube
- **Infrastructure as Code**: Terraform (AWS EKS)
- **CI/CD**: GitHub Actions, GitHub Container Registry (GHCR)

---

## 6. Local Setup
```bash
# Clone Repository
git clone https://github.com/username/cloudpulse.git
cd cloudpulse

# Create Virtual Environment & Install Dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
make install

# Execute Complete Pytest Test Suite
make test
```

---

## 7. Docker Compose Setup
```bash
# Launch full local stack (Services, Postgres, RabbitMQ, Prometheus, Grafana)
make docker-up

# Verify Running Services
docker compose ps

# Access Web Interfaces:
# - Auth Service:      http://localhost:8001/docs
# - Order Service:     http://localhost:8002/docs
# - Inventory Service: http://localhost:8003/docs
# - RabbitMQ Manager:  http://localhost:15672 (guest/guest)
# - Prometheus UI:     http://localhost:9090
# - Grafana Dashboard: http://localhost:3000 (admin/admin)

# Stop Stack
make docker-down
```

---

## 8. Minikube Setup
```bash
# Start Minikube cluster
minikube start --memory=4096 --cpus=2

# Point terminal to Minikube's Docker daemon
eval $(minikube docker-env)

# Build service images in Minikube Docker environment
docker build -t cloudpulse-auth:v0.1.0 -f services/auth_service/Dockerfile .
docker build -t cloudpulse-order:v0.1.0 -f services/order_service/Dockerfile .
docker build -t cloudpulse-inventory:v0.1.0 -f services/inventory_service/Dockerfile .
```

---

## 9. Kubernetes Deployment
```bash
# Apply all Kubernetes manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmaps/
kubectl apply -f k8s/secrets/
kubectl apply -f k8s/postgres/
kubectl apply -f k8s/rabbitmq/
kubectl apply -f k8s/auth_service/
kubectl apply -f k8s/order_service/
kubectl apply -f k8s/inventory_service/
kubectl apply -f k8s/prometheus/
kubectl apply -f k8s/grafana/
kubectl apply -f k8s/hpa/
kubectl apply -f k8s/rbac.yaml

# Check Pod Status
kubectl get pods -n cloudpulse
```

---

## 10. Prometheus & Grafana Setup
- **Prometheus** scrapes targets every 5 seconds via target declarations in `monitoring/prometheus/prometheus.yml`.
- **Grafana** automatically provisions datasources and pre-configures the `CloudPulse System Overview & Self-Healing Dashboard` displaying request rates, latency p95, HTTP errors, ML anomaly scores, and remediation triggers.

---

## 11. ML Training
```bash
# Train Isolation Forest model on metric feature vectors
python -m ml.training.train

# Output artifacts saved to:
# - ml/models/isolation_forest.pkl
# - ml/models/scaler.pkl
# - ml/models/model_metadata.json
# - ml/data/synthetic_metrics.csv
```

---

## 12. Remediation Controller
The remediation controller (`remediation/controller.py`) enforces strict safety policies:
- **Confidence Threshold**: Requires anomaly score >= 0.75.
- **Cooldown Window**: Minimum 180s delay between actions on the same workload.
- **Allowlist**: Only target microservices (`auth-service`, `order-service`, `inventory-service`).
- **Hourly Rate Limit**: Maximum 3 remediations per hour per workload.

---

## 13. Chaos Testing
```bash
# Simulate pod termination fault injection
python chaos/chaos.py --kill-pod order-service --namespace cloudpulse

# Dry-run validation
python chaos/chaos.py --kill-pod order-service --dry-run
```

---

## 14. Full Self-Healing Demo
Run the automated end-to-end self-healing demonstration:
```bash
python demo.py
```

Expected Output Sequence:
```text
[STEP 1] NORMAL BASELINE OPERATION -> ML Anomaly Score: 0.13 (HEALTHY)
[STEP 2] CHAOS FAULT INJECTION -> Latency P95 spiked: 9800ms, Error Rate: 45.0%
[STEP 3] ML ANOMALY DETECTION -> Isolation Forest Score: 0.97 (ANOMALY DETECTED)
[STEP 4] REMEDIATION CONTROLLER -> Guardrail Check PASSED
[STEP 5] KUBERNETES REMEDIATION -> Action Executed: Target pod recycled via K8s API
[STEP 6] SYSTEM RECOVERY -> Post-Remediation ML Anomaly Score: 0.13 (RECOVERED)
```

---

## 15. AWS EKS Deployment (Terraform)
> **WARNING**: EKS incurs charges on your AWS account (~$73/mo control plane + EC2 compute).

```bash
cd terraform/
terraform init
terraform plan
terraform apply
```
See [`terraform/README.md`](file:///c:/Users/kesha/OneDrive/Desktop/CloudPulse/terraform/README.md) for full cost details.

---

## 16. CI/CD
GitHub Actions workflows located in `.github/workflows/`:
- `test.yml`: Automated pytest execution on push/PR.
- `build.yml`: Builds Docker images and publishes to GitHub Container Registry (`ghcr.io`).
- `deploy.yml`: Deploys updated manifests to Kubernetes cluster and verifies rollout status.

---

## 17. Troubleshooting
```bash
# View microservice logs
docker compose logs -f order-service

# Check Kubernetes pod events
kubectl describe pod -l app=order-service -n cloudpulse

# Reset local database caches
make clean
```

---

## 18. Security Considerations
- **Non-Root Execution**: Container images run as unprivileged `appuser` (UID 10001).
- **No Plaintext Passwords**: Password hashing via `bcrypt`.
- **JWT Authentication**: HS256 JWT tokens with configurable secret & expiration.
- **RBAC Minimal Privileges**: Remediation controller service account is restricted via Role & RoleBinding.
- **No Hardcoded Secrets**: Secrets injected via environment variables & K8s Secrets.

---

## 19. Limitations
- Unsupervised Isolation Forest detects anomalies based on time-series deviations, not deterministic root-cause diagnosis.
- In-memory SQLite fallback used during unit tests for speed; PostgreSQL required for multi-pod concurrency.

---

## 20. Future Improvements
- OpenTelemetry distributed tracing with Jaeger.
- Kafka for high-throughput event streaming.
- LSTM/Transformer-based predictive failure modeling.
- Canary deployment rollbacks via ArgoCD.
