output "bucket_id" {
  description = "ID of the S3 bucket"
  value       = aws_s3_bucket.static_site.id
}

output "bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.static_site.arn
}

output "website_endpoint" {
  description = "Website endpoint URL"
  value       = aws_s3_bucket_website_configuration.static_site.website_endpoint
}

output "website_domain" {
  description = "Website domain"
  value       = aws_s3_bucket_website_configuration.static_site.website_domain
}

