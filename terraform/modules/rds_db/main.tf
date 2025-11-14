# RDS Database Module for Diagram Maker
# Purpose: PostgreSQL database for storing user diagram drafts and metadata
# Includes: subnet group, security group, parameter group, RDS instance

# DB Subnet Group - defines which subnets the RDS instance can be placed in
# Multi-AZ deployment requires subnets in at least 2 different availability zones
resource "aws_db_subnet_group" "diagram_maker_db_subnet_group" {
  name       = "diagram-maker-db-subnet-${var.environment}"
  subnet_ids = var.subnet_ids

  tags = {
    Name        = "diagram-maker-db-subnet-${var.environment}"
    Environment = var.environment
  }
}

# Security Group - controls network access to the RDS instance
# Allows PostgreSQL traffic (port 5432) from specified sources
resource "aws_security_group" "diagram_maker_db_sg" {
  name        = "diagram-maker-db-sg-${var.environment}"
  description = "Security group for Diagram Maker RDS PostgreSQL instance"
  vpc_id      = var.vpc_id

  # Ingress rule - allow PostgreSQL traffic from application security group
  ingress {
    description     = "PostgreSQL access from application"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = var.allowed_security_groups  # EC2 instance security group
  }

  # Optional: Allow access from specific CIDR blocks (e.g., for development)
  dynamic "ingress" {
    for_each = var.allowed_cidr_blocks
    content {
      description = "PostgreSQL access from CIDR block"
      from_port   = 5432
      to_port     = 5432
      protocol    = "tcp"
      cidr_blocks = [ingress.value]
    }
  }

  # Egress rule - allow all outbound traffic (required for updates, backups)
  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "diagram-maker-db-sg-${var.environment}"
    Environment = var.environment
  }
}

# DB Parameter Group - PostgreSQL configuration tuning
# Optimized for application workload with JSON support
resource "aws_db_parameter_group" "diagram_maker_db_params" {
  name   = "diagram-maker-db-params-${var.environment}"
  family = var.db_parameter_group_family  # e.g., "postgres16"

  description = "Parameter group for Diagram Maker PostgreSQL database"

  # Enable auto_explain for slow query logging
  parameter {
    name  = "log_statement"
    value = "all"
    apply_method = "pending-reboot"
  }

  # Optimize for JSON operations (storing mermaid code, metadata)
  parameter {
    name  = "shared_preload_libraries"
    value = "pg_stat_statements"
    apply_method = "pending-reboot"
  }

  tags = {
    Name        = "diagram-maker-db-params-${var.environment}"
    Environment = var.environment
  }
}

# RDS Instance - The actual PostgreSQL database
resource "aws_db_instance" "diagram_maker_db" {
  identifier = "diagram-maker-db-${var.environment}"

  # Database Engine Configuration
  engine               = "postgres"
  engine_version       = var.db_engine_version  # e.g., "16.1"
  instance_class       = var.db_instance_class  # e.g., "db.t3.micro" for dev
  allocated_storage    = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage  # Enable storage autoscaling
  storage_type         = "gp3"  # General Purpose SSD (latest generation)
  storage_encrypted    = true   # Encrypt data at rest

  # Database Credentials
  db_name  = var.db_name
  username = var.db_username
  password = var.db_password  # Should be provided via AWS Secrets Manager or environment variable

  # Network Configuration
  db_subnet_group_name   = aws_db_subnet_group.diagram_maker_db_subnet_group.name
  vpc_security_group_ids = [aws_security_group.diagram_maker_db_sg.id]
  publicly_accessible    = var.publicly_accessible  # Default: false (private)

  # High Availability
  multi_az = var.multi_az  # Enable multi-AZ for production

  # Backup Configuration
  backup_retention_period = var.backup_retention_days  # Number of days to retain backups
  backup_window           = var.backup_window          # Preferred backup time (UTC)
  maintenance_window      = var.maintenance_window     # Preferred maintenance window

  # Performance and Monitoring
  parameter_group_name           = aws_db_parameter_group.diagram_maker_db_params.name
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]  # Export logs to CloudWatch
  # Enhanced monitoring: only enable if monitoring_role_arn is provided
  monitoring_interval            = var.monitoring_role_arn != "" ? 60 : 0  # 0 = disabled, 60 = every 60 seconds
  monitoring_role_arn            = var.monitoring_role_arn != "" ? var.monitoring_role_arn : null
  performance_insights_enabled   = var.enable_performance_insights

  # Deletion Protection
  deletion_protection = var.deletion_protection  # Prevent accidental deletion in production
  skip_final_snapshot = var.skip_final_snapshot  # Set to false for production
  final_snapshot_identifier = var.skip_final_snapshot ? null : "diagram-maker-db-final-snapshot-${var.environment}-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"

  # Apply changes immediately or during maintenance window
  apply_immediately = var.apply_immediately

  tags = {
    Name        = "diagram-maker-db-${var.environment}"
    Environment = var.environment
    Purpose     = "User diagram drafts storage"
  }
}
