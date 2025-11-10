output "bucket_id" {
  description = "ID of the S3 bucket for knowledge base documents"
  value       = aws_s3_bucket.diagram_maker_kb.id
}

output "bucket_arn" {
  description = "ARN of the S3 bucket for knowledge base documents"
  value       = aws_s3_bucket.diagram_maker_kb.arn
}

output "bucket_domain_name" {
  description = "Domain name of the S3 bucket"
  value       = aws_s3_bucket.diagram_maker_kb.bucket_domain_name
}

output "uploads_prefix" {
  description = "Prefix path for uploads"
  value       = "uploads/"
}

output "corpus_prefix" {
  description = "Prefix path for processed corpus documents"
  value       = "corpus/"
}

output "archive_prefix" {
  description = "Prefix path for archived documents"
  value       = "archive/"
}

