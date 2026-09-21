# =============================================================================
# NAVAM — Terraform Module: AWS RDS (PostgreSQL 16 + PostGIS)
# Multi-AZ, encrypted, 35-day backups, deletion protection
# =============================================================================

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.50"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

# ---------------------------------------------------------------------------
# Variables
# ---------------------------------------------------------------------------
variable "identifier" {
  description = "RDS instance identifier"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for the DB subnet group"
  type        = list(string)
}

variable "eks_node_sg_id" {
  description = "EKS worker node security group ID (allowed to connect to RDS)"
  type        = string
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "navam"
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "navam"
}

variable "db_password" {
  description = "Database master password (retrieved from Secrets Manager)"
  type        = string
  sensitive   = true
}

variable "instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.r6g.large"
}

variable "allocated_storage" {
  description = "Initial storage in GB"
  type        = number
  default     = 100
}

variable "max_allocated_storage" {
  description = "Maximum storage in GB (autoscaling upper bound)"
  type        = number
  default     = 500
}

variable "multi_az" {
  description = "Enable Multi-AZ deployment"
  type        = bool
  default     = true
}

variable "kms_key_id" {
  description = "KMS key ARN for storage encryption"
  type        = string
}

# ---------------------------------------------------------------------------
# Security Group — only EKS nodes can reach port 5432
# ---------------------------------------------------------------------------
resource "aws_security_group" "rds" {
  name        = "${var.identifier}-rds-sg"
  description = "Security group for NAVAM RDS instance — allows PostgreSQL from EKS nodes only"
  vpc_id      = var.vpc_id

  ingress {
    description     = "PostgreSQL from EKS worker nodes"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.eks_node_sg_id]
  }

  egress {
    description = "Allow all outbound (RDS needs to reach AWS endpoints)"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.identifier}-rds-sg"
    Environment = var.environment
  }
}

# ---------------------------------------------------------------------------
# DB Subnet Group — private subnets only
# ---------------------------------------------------------------------------
resource "aws_db_subnet_group" "navam" {
  name        = "${var.identifier}-subnet-group"
  description = "NAVAM RDS subnet group (private subnets across 3 AZs)"
  subnet_ids  = var.private_subnet_ids

  tags = {
    Name        = "${var.identifier}-subnet-group"
    Environment = var.environment
  }
}

# ---------------------------------------------------------------------------
# DB Parameter Group
# PostgreSQL 16 with PostGIS-friendly settings
# ---------------------------------------------------------------------------
resource "aws_db_parameter_group" "navam" {
  name        = "${var.identifier}-pg16-params"
  family      = "postgres16"
  description = "NAVAM PostgreSQL 16 parameter group with PostGIS optimisations"

  # Enable PostGIS and topology
  parameter {
    name  = "shared_preload_libraries"
    value = "pg_stat_statements,pg_trgm"
  }

  # Memory settings — tuned for r6g.large (16GB RAM)
  parameter {
    name  = "shared_buffers"
    value = "262144"  # 256MB in 8kB pages
    apply_method = "pending-reboot"
  }

  parameter {
    name  = "work_mem"
    value = "65536"   # 64MB in kB
  }

  parameter {
    name  = "maintenance_work_mem"
    value = "524288"  # 512MB in kB
    apply_method = "pending-reboot"
  }

  parameter {
    name  = "effective_cache_size"
    value = "3145728" # 3GB in 8kB pages
  }

  # WAL / replication settings
  parameter {
    name  = "wal_level"
    value = "replica"
    apply_method = "pending-reboot"
  }

  parameter {
    name  = "max_wal_senders"
    value = "10"
    apply_method = "pending-reboot"
  }

  # Slow query logging (log queries > 1s)
  parameter {
    name  = "log_min_duration_statement"
    value = "1000"
  }

  parameter {
    name  = "log_connections"
    value = "1"
  }

  parameter {
    name  = "log_disconnections"
    value = "1"
  }

  # Checkpointing
  parameter {
    name  = "checkpoint_completion_target"
    value = "0.9"
  }

  parameter {
    name  = "random_page_cost"
    value = "1.1"  # SSD storage (gp3)
  }

  tags = {
    Name        = "${var.identifier}-pg16-params"
    Environment = var.environment
  }
}

# ---------------------------------------------------------------------------
# RDS Instance — PostgreSQL 16 (Multi-AZ, encrypted, 35-day backups)
# ---------------------------------------------------------------------------
resource "aws_db_instance" "navam" {
  # Identification
  identifier = var.identifier

  # Engine
  engine               = "postgres"
  engine_version       = "16.3"
  instance_class       = var.instance_class

  # Storage — gp3 for consistent IOPS
  storage_type          = "gp3"
  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage  # Auto-scaling enabled
  storage_encrypted     = true
  kms_key_id            = var.kms_key_id

  # Credentials
  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  # Networking
  db_subnet_group_name   = aws_db_subnet_group.navam.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false  # Never expose to internet

  # High availability
  multi_az               = var.multi_az

  # Configuration
  parameter_group_name = aws_db_parameter_group.navam.name

  # Backup and maintenance
  backup_retention_period   = 35                 # 35 days (MeitY compliance)
  backup_window             = "01:00-02:00"      # IST 06:30–07:30
  maintenance_window        = "sun:02:00-sun:04:00"
  copy_tags_to_snapshot     = true
  delete_automated_backups  = false

  # Performance Insights
  performance_insights_enabled          = true
  performance_insights_retention_period = 7   # Days (free tier: 7)
  performance_insights_kms_key_id       = var.kms_key_id

  # Enhanced monitoring (60s interval)
  monitoring_interval = 60
  monitoring_role_arn = aws_iam_role.rds_enhanced_monitoring.arn

  # CloudWatch log exports
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  # Deletion protection — prevent accidental drops
  deletion_protection = true
  skip_final_snapshot = false
  final_snapshot_identifier = "${var.identifier}-final-snapshot-${formatdate("YYYYMMDD", timestamp())}"

  # Auto minor version upgrades (security patches)
  auto_minor_version_upgrade = true

  # Apply changes immediately in staging, deferred in production
  apply_immediately = var.environment != "production"

  tags = {
    Name        = var.identifier
    Environment = var.environment
    Service     = "database"
    Engine      = "PostgreSQL-16-PostGIS"
  }

  lifecycle {
    # Never destroy production database
    prevent_destroy = true
    # Ignore password changes (managed externally via Secrets Manager rotation)
    ignore_changes = [password]
  }
}

# ---------------------------------------------------------------------------
# IAM Role for RDS Enhanced Monitoring
# ---------------------------------------------------------------------------
data "aws_iam_policy_document" "rds_monitoring_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["monitoring.rds.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "rds_enhanced_monitoring" {
  name               = "${var.identifier}-rds-monitoring"
  assume_role_policy = data.aws_iam_policy_document.rds_monitoring_assume.json

  tags = {
    Name        = "${var.identifier}-rds-monitoring"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy_attachment" "rds_enhanced_monitoring" {
  role       = aws_iam_role.rds_enhanced_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# ---------------------------------------------------------------------------
# CloudWatch Alarms
# ---------------------------------------------------------------------------
resource "aws_cloudwatch_metric_alarm" "rds_cpu_high" {
  alarm_name          = "${var.identifier}-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "RDS CPU > 80% for 15 minutes"
  alarm_actions       = []  # Add SNS ARN for PagerDuty/Slack alerts

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.navam.id
  }

  tags = {
    Environment = var.environment
  }
}

resource "aws_cloudwatch_metric_alarm" "rds_storage_low" {
  alarm_name          = "${var.identifier}-storage-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 10737418240  # 10 GB in bytes
  alarm_description   = "RDS free storage < 10 GB"
  alarm_actions       = []

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.navam.id
  }

  tags = {
    Environment = var.environment
  }
}

# ---------------------------------------------------------------------------
# Outputs
# ---------------------------------------------------------------------------
output "endpoint" {
  description = "RDS instance endpoint (host:port)"
  value       = aws_db_instance.navam.endpoint
  sensitive   = true
}

output "address" {
  description = "RDS instance hostname"
  value       = aws_db_instance.navam.address
  sensitive   = true
}

output "port" {
  description = "RDS instance port"
  value       = aws_db_instance.navam.port
}

output "db_name" {
  description = "Database name"
  value       = aws_db_instance.navam.db_name
}

output "db_username" {
  description = "Database master username"
  value       = aws_db_instance.navam.username
  sensitive   = true
}

output "resource_id" {
  description = "RDS resource ID (for IAM auth)"
  value       = aws_db_instance.navam.resource_id
}

output "security_group_id" {
  description = "RDS security group ID"
  value       = aws_security_group.rds.id
}
