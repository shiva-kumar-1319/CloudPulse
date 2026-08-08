variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "Target AWS region for CloudPulse infrastructure"
}

variable "environment" {
  type        = string
  default     = "dev"
  description = "Environment name (dev, prod)"
}

variable "cluster_name" {
  type        = string
  default     = "cloudpulse-eks-cluster"
  description = "EKS Cluster identifier"
}

variable "node_instance_type" {
  type        = string
  default     = "t3.medium"
  description = "EC2 Instance type for EKS managed node group"
}

variable "desired_capacity" {
  type        = number
  default     = 2
  description = "Desired number of worker nodes"
}

variable "min_capacity" {
  type        = number
  default     = 1
  description = "Minimum number of worker nodes"
}

variable "max_capacity" {
  type        = number
  default     = 4
  description = "Maximum number of worker nodes"
}
