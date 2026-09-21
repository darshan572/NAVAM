# =============================================================================
# NAVAM — Terraform Root Module
# AWS Mumbai (ap-south-1) | MeitY-empanelled infrastructure
# GitOps: all changes via PRs — no manual console changes in production.
# =============================================================================

terraform {
  required_version = ">= 1.8.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.50"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.30"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.13"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  # Remote state backend — S3 + DynamoDB locking
  # Create the bucket and table manually once, then configure here.
  backend "s3" {
    bucket         = "navam-terraform-state-ap-south-1"   # Replace with actual bucket name
    key            = "infra/terraform.tfstate"
    region         = "ap-south-1"
    encrypt        = true
    kms_key_id     = "alias/navam-terraform-state"        # Replace with actual KMS alias
    dynamodb_table = "navam-terraform-locks"
  }
}

# ---------------------------------------------------------------------------
# Provider configuration
# ---------------------------------------------------------------------------
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "NAVAM"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Team        = "TheSixSense"
      CostCenter  = "SIH2026"
    }
  }
}

provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)

  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
  }
}

provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)

    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
    }
  }
}

# ---------------------------------------------------------------------------
# Local values
# ---------------------------------------------------------------------------
locals {
  cluster_name = "navam-${var.environment}-${var.aws_region}"
  common_tags = {
    Project     = "NAVAM"
    Environment = var.environment
  }
}

# ---------------------------------------------------------------------------
# Module: VPC
# Creates: VPC, public/private subnets (3 AZs), NAT gateway, route tables
# ---------------------------------------------------------------------------
module "vpc" {
  source = "./modules/vpc"

  name               = "navam-${var.environment}"
  environment        = var.environment
  aws_region         = var.aws_region
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
  private_subnets    = var.private_subnets
  public_subnets     = var.public_subnets

  # EKS requires these tags on subnets
  private_subnet_tags = {
    "kubernetes.io/cluster/${local.cluster_name}" = "shared"
    "kubernetes.io/role/internal-elb"             = "1"
  }
  public_subnet_tags = {
    "kubernetes.io/cluster/${local.cluster_name}" = "shared"
    "kubernetes.io/role/elb"                      = "1"
  }
}

# ---------------------------------------------------------------------------
# Module: EKS
# Creates: EKS cluster, managed node groups, IRSA, addons
# ---------------------------------------------------------------------------
module "eks" {
  source = "./modules/eks"

  cluster_name    = local.cluster_name
  cluster_version = "1.30"
  environment     = var.environment
  aws_region      = var.aws_region

  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  public_subnet_ids  = module.vpc.public_subnet_ids

  # Node group configuration
  node_groups = {
    application = {
      instance_types = ["t3.large"]
      capacity_type  = "ON_DEMAND"
      min_size       = 2
      max_size       = 10
      desired_size   = 3
      labels = {
        role = "application"
      }
      taints = []
    }
    gpu = {
      instance_types = ["g4dn.xlarge"]
      capacity_type  = "SPOT"
      min_size       = 0
      max_size       = 3
      desired_size   = 0
      labels = {
        role                     = "gpu"
        "nvidia.com/gpu.present" = "true"
      }
      taints = [
        {
          key    = "nvidia.com/gpu"
          value  = "true"
          effect = "NO_SCHEDULE"
        }
      ]
    }
  }
}

# ---------------------------------------------------------------------------
# Module: RDS (PostgreSQL 16 + PostGIS)
# ---------------------------------------------------------------------------
module "rds" {
  source = "./modules/rds"

  identifier        = "navam-${var.environment}"
  environment       = var.environment
  aws_region        = var.aws_region
  vpc_id            = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  eks_node_sg_id    = module.eks.node_security_group_id

  db_name   = "navam"
  db_username = "navam"
  # Password retrieved from AWS Secrets Manager — not hardcoded
  db_password = data.aws_secretsmanager_secret_version.db_password.secret_string

  instance_class    = var.rds_instance_class
  allocated_storage = 100
  multi_az          = var.environment == "production"
  kms_key_id        = module.kms.rds_key_arn
}

# ---------------------------------------------------------------------------
# Module: ElastiCache (Redis 7)
# ---------------------------------------------------------------------------
module "elasticache" {
  source = "./modules/elasticache"

  name               = "navam-${var.environment}"
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  eks_node_sg_id     = module.eks.node_security_group_id

  node_type          = var.redis_node_type
  num_cache_nodes    = var.environment == "production" ? 2 : 1
  kms_key_id         = module.kms.elasticache_key_arn
}

# ---------------------------------------------------------------------------
# Module: MSK (Managed Kafka)
# ---------------------------------------------------------------------------
module "msk" {
  source = "./modules/msk"

  cluster_name       = "navam-${var.environment}"
  environment        = var.environment
  kafka_version      = "3.6.0"
  number_of_broker_nodes = var.environment == "production" ? 3 : 1
  broker_instance_type   = var.kafka_instance_type
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  eks_node_sg_id     = module.eks.node_security_group_id
  kms_key_id         = module.kms.msk_key_arn
}

# ---------------------------------------------------------------------------
# Module: S3 (artifact and data storage)
# ---------------------------------------------------------------------------
module "s3" {
  source = "./modules/s3"

  environment = var.environment
  aws_region  = var.aws_region
  kms_key_id  = module.kms.s3_key_arn

  buckets = {
    mlflow_artifacts = "navam-mlflow-artifacts-${var.environment}"
    raw_data         = "navam-raw-data-${var.environment}"
    processed_data   = "navam-processed-data-${var.environment}"
    terraform_state  = "navam-terraform-state-${var.aws_region}"  # Already exists
  }
}

# ---------------------------------------------------------------------------
# Module: KMS (encryption keys for all services)
# ---------------------------------------------------------------------------
module "kms" {
  source = "./modules/kms"

  environment = var.environment
  aws_region  = var.aws_region
}

# ---------------------------------------------------------------------------
# Data sources
# ---------------------------------------------------------------------------
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "navam/${var.environment}/db-password"
}

# ---------------------------------------------------------------------------
# Variables
# ---------------------------------------------------------------------------
variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "ap-south-1"
}

variable "environment" {
  description = "Deployment environment (staging | production)"
  type        = string
  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "Environment must be 'staging' or 'production'."
  }
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones to use"
  type        = list(string)
  default     = ["ap-south-1a", "ap-south-1b", "ap-south-1c"]
}

variable "private_subnets" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "public_subnets" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

variable "rds_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.r6g.large"
}

variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.r6g.large"
}

variable "kafka_instance_type" {
  description = "MSK broker instance type"
  type        = string
  default     = "kafka.m5.large"
}

# ---------------------------------------------------------------------------
# Outputs
# ---------------------------------------------------------------------------
output "eks_cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  description = "EKS API server endpoint"
  value       = module.eks.cluster_endpoint
  sensitive   = true
}

output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = module.rds.endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = module.elasticache.primary_endpoint
  sensitive   = true
}

output "kafka_bootstrap_brokers" {
  description = "MSK broker connection string"
  value       = module.msk.bootstrap_brokers_tls
  sensitive   = true
}

output "mlflow_artifacts_bucket" {
  description = "S3 bucket for MLflow artifacts"
  value       = module.s3.bucket_ids["mlflow_artifacts"]
}
