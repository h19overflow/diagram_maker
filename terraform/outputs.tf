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

