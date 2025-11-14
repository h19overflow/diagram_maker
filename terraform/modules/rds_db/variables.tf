# Variables for RDS PostgreSQL Database Module

variable "environment" {
  type        = string
  description = "Environment name (e.g., dev, staging, prod)"
  default     = "dev"
}

# Database Engine Configuration
variable "db_engine_version" {
  type        = string
  description = "PostgreSQL engine version (AWS RDS format, e.g., 16.11, 17.6)"
  default     = "16.11"
}

variable "db_instance_class" {
  type        = string
  description = "RDS instance type (e.g., db.t3.micro, db.t3.small, db.r5.large)"
  default     = "db.t3.micro"
}

variable "db_parameter_group_family" {
  type        = string
  description = "DB parameter group family (must match engine version, e.g., postgres16)"
  default     = "postgres16"
}

# Storage Configuration
variable "db_allocated_storage" {
  type        = number
  description = "Initial allocated storage in GB"
  default     = 20
}

variable "db_max_allocated_storage" {
  type        = number
  description = "Maximum storage for autoscaling in GB (0 to disable)"
  default     = 100
}

# Database Credentials
variable "db_name" {
  type        = string
  description = "Name of the initial database to create"
  default     = "diagram_maker"
}

variable "db_username" {
  type        = string
  description = "Master username for the database"
  default     = "diagram_maker_admin"
}

variable "db_password" {
  type        = string
  description = "Master password for the database (should be provided via AWS Secrets Manager or secure variable)"
  sensitive   = true
}

# Network Configuration
variable "vpc_id" {
  type        = string
  description = "VPC ID where the RDS instance will be deployed"
}

variable "subnet_ids" {
  type        = list(string)
  description = "List of subnet IDs for the DB subnet group (requires at least 2 subnets in different AZs)"
}

variable "allowed_security_groups" {
  type        = list(string)
  description = "List of security group IDs allowed to access the database (e.g., EC2 application security group)"
  default     = []
}

variable "allowed_cidr_blocks" {
  type        = list(string)
  description = "List of CIDR blocks allowed to access the database (optional, for development access)"
  default     = []
}

variable "publicly_accessible" {
  type        = bool
  description = "Whether the database should be publicly accessible (should be false for production)"
  default     = false
}

# High Availability
variable "multi_az" {
  type        = bool
  description = "Enable multi-AZ deployment for high availability (recommended for production)"
  default     = false
}

# Backup Configuration
variable "backup_retention_days" {
  type        = number
  description = "Number of days to retain automated backups (0 to disable, 1-35 days)"
  default     = 7
}

variable "backup_window" {
  type        = string
  description = "Preferred backup window in UTC (format: hh24:mi-hh24:mi, e.g., 03:00-04:00)"
  default     = "03:00-04:00"
}

variable "maintenance_window" {
  type        = string
  description = "Preferred maintenance window in UTC (format: ddd:hh24:mi-ddd:hh24:mi, e.g., mon:04:00-mon:05:00)"
  default     = "mon:04:00-mon:05:00"
}

# Monitoring
variable "monitoring_role_arn" {
  type        = string
  description = "IAM role ARN for enhanced monitoring (leave empty to disable enhanced monitoring)"
  default     = ""
}

variable "enable_performance_insights" {
  type        = bool
  description = "Enable Performance Insights for database performance monitoring"
  default     = false
}

# Deletion Protection
variable "deletion_protection" {
  type        = bool
  description = "Enable deletion protection to prevent accidental database deletion"
  default     = true
}

variable "skip_final_snapshot" {
  type        = bool
  description = "Skip final snapshot when deleting the database (should be false for production)"
  default     = false
}

# Apply Changes
variable "apply_immediately" {
  type        = bool
  description = "Apply changes immediately or during the next maintenance window"
  default     = false
}
