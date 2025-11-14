# Data source to get default VPC
data "aws_vpc" "default" {
  default = true
}

# Data source to get default subnets in the default VPC
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

module "s3_frontend" {
  source = "./modules/s3_frontend"

  bucket_name    = "diagram-maker-frontend-${var.environment}"
  environment    = var.environment
  index_document = "index.html"
  error_document = "404.html"
}

module "s3_kb" {
  source = "./modules/s3_kb"
  
  bucket_name              = "diagram-maker-kb-${var.environment}"
  environment              = var.environment
  enable_lifecycle_rules   = true
  archive_after_days       = 90
  expire_archive_after_days = 365
}

module "ecr" {
  source = "./modules/ecr"
  environment = var.environment
  resource_prefix = var.resource_prefix
}

module "app_instance" {
  source = "./modules/app_instance"
  environment         = var.environment
  s3_bucket_name      = module.s3_kb.bucket_id
  instance_name       = "diagram-maker-app-${var.environment}"
  ecr_repository_name = "${var.resource_prefix}-diagram-maker-ecr-repo"  # Scopes ECR permissions to this repo

  # Optional: Enable RDS IAM authentication (more secure than password-based auth)
  # enable_rds_iam_auth = true
  # rds_resource_id     = module.rds_db.db_instance_resource_id
}

# RDS Database Module for User Diagram Drafts
module "rds_db" {
  source = "./modules/rds_db"

  environment = var.environment

  # Network Configuration (using default VPC for dev)
  vpc_id     = data.aws_vpc.default.id
  subnet_ids = data.aws_subnets.default.ids

  # Security: Allow EC2 instance to access database
  # Note: You'll need to add security group ID from app_instance module
  # For now, using CIDR blocks (less secure, for dev only)
  allowed_cidr_blocks = ["0.0.0.0/0"]  # WARNING: Replace with specific CIDR for production

  # Database Credentials
  db_name     = "diagram_maker"
  db_username = "diagram_maker_admin"
  db_password = var.db_password  # Pass via: terraform apply -var="db_password=YourPassword123"

  # Database Configuration
  db_instance_class       = "db.t3.micro"  # Free tier eligible
  db_allocated_storage    = 20
  db_max_allocated_storage = 100

  # Development Settings (change for production)
  multi_az            = false  # Set to true for production (high availability)
  deletion_protection = false  # Set to true for production
  skip_final_snapshot = true   # Set to false for production
  publicly_accessible = false  # Keep false (private database)

  # Backup Configuration
  backup_retention_days = 7
  backup_window         = "03:00-04:00"
  maintenance_window    = "mon:04:00-mon:05:00"
}