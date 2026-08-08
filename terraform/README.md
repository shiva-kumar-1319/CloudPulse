# CloudPulse AWS EKS Infrastructure as Code (Terraform)

This directory contains production-ready Terraform modules for provisioning an AWS EKS Cluster, managed EC2 node groups (`t3.medium`), VPC networking, Subnets, Internet Gateway, Route Tables, and IAM roles.

---

## ⚠️ CLOUD COST WARNING & ESTIMATION TABLE

> **IMPORTANT**: Deploying CloudPulse to AWS EKS will incur charges on your AWS bill. The primary free demonstration environment is local **Minikube** ($0 cost).

| Component | Local (Minikube) | Cloud Target (AWS) | Potential Monthly Cost |
|-----------|------------------|--------------------|------------------------|
| Microservices | Minikube Pods | EKS Worker Nodes (`t3.medium`) | ~$30 - $60 / month |
| EKS Control Plane | Minikube | Managed AWS EKS | ~$73 / month ($0.10/hr) |
| RabbitMQ | Docker Container | Containerized on EKS | Included in EC2 compute |
| PostgreSQL | Docker Container | Containerized or AWS RDS | ~$15 - $50 / month (if RDS) |
| Monitoring Stack | Prometheus/Grafana | Containerized on EKS | Included in EC2 compute |
| Infrastructure | Free | Terraform CLI | Free tool |

---

## 🚀 Deployment Instructions

### 1. Initialize Terraform
```bash
cd terraform/
terraform init
```

### 2. Plan Infrastructure Provisioning
```bash
terraform plan -out=tfplan
```

### 3. Apply Provisioning
```bash
terraform apply tfplan
```

### 4. Configure `kubectl` for EKS Cluster
```bash
aws eks update-kubeconfig --name cloudpulse-eks-cluster --region us-east-1
```

### 5. Destroy Infrastructure (To avoid ongoing AWS charges)
```bash
terraform destroy -auto-approve
```
