# RDS Database Module Configuration
# VPC and Network Configuration
vpc_id = "vpc-09ca1190935609858"
subnet_ids = [
  "subnet-06b417fb4146566eb",  # ap-southeast-2a
  "subnet-01e3b10f3b8f0a0f5"   # ap-southeast-2c
]

# Environment
environment = "dev"

# Database Credentials
# Note: For security, set db_password via environment variable:
# export TF_VAR_db_password="YourSecurePassword123"
# Or pass via command line: terraform apply -var="db_password=YourPassword"

# Database Configuration
db_engine_version       = "16.11"  # PostgreSQL 16.11 (latest stable 16.x)
db_instance_class       = "db.t3.micro"
db_allocated_storage    = 20
db_max_allocated_storage = 100

# Development Settings
multi_az            = false
deletion_protection = false
skip_final_snapshot = true
publicly_accessible = false

# Backup Configuration
backup_retention_days = 7
backup_window         = "03:00-04:00"
maintenance_window    = "mon:04:00-mon:05:00"

# Security (for development - allow all IPs)
# WARNING: Replace with specific security groups for production
allowed_cidr_blocks = ["0.0.0.0/0"]

