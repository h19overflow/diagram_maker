output "frontend_bucket_id" {
  description = "Frontend S3 bucket ID"
  value       = module.s3_frontend.bucket_id
}

output "frontend_bucket_arn" {
  description = "Frontend S3 bucket ARN"
  value       = module.s3_frontend.bucket_arn
}

output "frontend_website_endpoint" {
  description = "Frontend website endpoint URL"
  value       = module.s3_frontend.website_endpoint
}

output "frontend_website_domain" {
  description = "Frontend website domain"
  value       = module.s3_frontend.website_domain
}

output "kb_bucket_id" {
  description = "Knowledge base S3 bucket ID"
  value       = module.s3_kb.bucket_id
}

output "kb_bucket_arn" {
  description = "Knowledge base S3 bucket ARN"
  value       = module.s3_kb.bucket_arn
}

output "kb_bucket_domain_name" {
  description = "Knowledge base S3 bucket domain name"
  value       = module.s3_kb.bucket_domain_name
}

output "kb_uploads_prefix" {
  description = "Prefix path for uploads"
  value       = module.s3_kb.uploads_prefix
}

output "kb_corpus_prefix" {
  description = "Prefix path for processed corpus documents"
  value       = module.s3_kb.corpus_prefix
}

output "kb_archive_prefix" {
  description = "Prefix path for archived documents"
  value       = module.s3_kb.archive_prefix
}

# RDS Database Outputs
output "db_instance_endpoint" {
  description = "RDS instance connection endpoint (hostname:port)"
  value       = module.rds_db.db_instance_endpoint
}

output "db_instance_address" {
  description = "RDS instance hostname"
  value       = module.rds_db.db_instance_address
}

output "db_instance_port" {
  description = "RDS instance port"
  value       = module.rds_db.db_instance_port
}

output "db_name" {
  description = "Database name"
  value       = module.rds_db.db_name
}

output "db_connection_string" {
  description = "PostgreSQL connection string (without password)"
  value       = module.rds_db.connection_string
  sensitive   = true
}

output "db_security_group_id" {
  description = "Security group ID for the RDS instance"
  value       = module.rds_db.db_security_group_id
}

