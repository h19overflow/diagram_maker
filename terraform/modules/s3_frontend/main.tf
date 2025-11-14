resource "aws_s3_bucket" "static_site" {
  bucket = var.bucket_name
}



resource "aws_s3_bucket_ownership_controls" "static_site" {
  bucket = aws_s3_bucket.static_site.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_public_access_block" "static_site" {
  bucket = aws_s3_bucket.static_site.id

  # Public access blocks disabled for static website hosting
  # Note: For production, consider using CloudFront with Origin Access Control
  # to keep the bucket private while serving content publicly
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_website_configuration" "static_site" {
  bucket = aws_s3_bucket.static_site.id

  index_document {
    suffix = var.index_document
  }

  error_document {
    key = var.error_document
  }
}

# Bucket policy for CloudFront access (only if CloudFront distribution exists)
# Note: This policy requires a CloudFront distribution to be created separately
# If you don't have CloudFront yet, comment out or remove this resource
# resource "aws_s3_bucket_policy" "static_site" {
#   bucket = aws_s3_bucket.static_site.id
#   depends_on = [aws_s3_bucket_public_access_block.static_site]
#
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [{
#       Sid    = "AllowCloudFrontOAC"
#       Effect = "Allow"
#       Principal = {
#         Service = "cloudfront.amazonaws.com"
#       }
#       Action   = "s3:GetObject"
#       Resource = "${aws_s3_bucket.static_site.arn}/*"
#       Condition = {
#         StringEquals = {
#           "AWS:SourceArn" = aws_cloudfront_distribution.static_site.arn
#         }
#       }
#     }]
#   })
# }
