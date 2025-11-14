# Outputs for RDS PostgreSQL Database Module
# These values are used by the application to connect to the database

output "db_instance_id" {
  description = "ID of the RDS instance"
  value       = aws_db_instance.diagram_maker_db.id
}

output "db_instance_arn" {
  description = "ARN of the RDS instance"
  value       = aws_db_instance.diagram_maker_db.arn
}

output "db_instance_endpoint" {
  description = "Connection endpoint for the database (hostname:port)"
  value       = aws_db_instance.diagram_maker_db.endpoint
}

output "db_instance_address" {
  description = "Hostname of the database instance (without port)"
  value       = aws_db_instance.diagram_maker_db.address
}

output "db_instance_port" {
  description = "Port number of the database instance"
  value       = aws_db_instance.diagram_maker_db.port
}

output "db_name" {
  description = "Name of the initial database"
  value       = aws_db_instance.diagram_maker_db.db_name
}

output "db_username" {
  description = "Master username for the database"
  value       = aws_db_instance.diagram_maker_db.username
  sensitive   = true
}

output "db_security_group_id" {
  description = "ID of the security group attached to the RDS instance"
  value       = aws_security_group.diagram_maker_db_sg.id
}

output "db_subnet_group_name" {
  description = "Name of the DB subnet group"
  value       = aws_db_subnet_group.diagram_maker_db_subnet_group.name
}

output "db_parameter_group_name" {
  description = "Name of the DB parameter group"
  value       = aws_db_parameter_group.diagram_maker_db_params.name
}

# Connection string for application use
output "connection_string" {
  description = "PostgreSQL connection string (without password) for application configuration"
  value       = "postgresql://${aws_db_instance.diagram_maker_db.username}@${aws_db_instance.diagram_maker_db.address}:${aws_db_instance.diagram_maker_db.port}/${aws_db_instance.diagram_maker_db.db_name}"
  sensitive   = true
}

# Monitoring and Management
output "db_instance_status" {
  description = "Status of the RDS instance"
  value       = aws_db_instance.diagram_maker_db.status
}

output "db_instance_resource_id" {
  description = "Resource ID of the RDS instance (used for IAM database authentication)"
  value       = aws_db_instance.diagram_maker_db.resource_id
}

output "cloudwatch_log_groups" {
  description = "CloudWatch log groups for the RDS instance"
  value       = aws_db_instance.diagram_maker_db.enabled_cloudwatch_logs_exports
}
