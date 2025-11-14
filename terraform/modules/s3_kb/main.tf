resource "aws_s3_bucket" "diagram_maker_kb" {
  bucket = var.bucket_name
}

resource "aws_s3_bucket_versioning" "diagram_maker_kb" {
  bucket = aws_s3_bucket.diagram_maker_kb.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_ownership_controls" "diagram_maker_kb" {
  bucket = aws_s3_bucket.diagram_maker_kb.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_public_access_block" "diagram_maker_kb" {
  bucket = aws_s3_bucket.diagram_maker_kb.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "diagram_maker_kb" {
  count  = var.enable_lifecycle_rules ? 1 : 0
  bucket = aws_s3_bucket.diagram_maker_kb.id

  rule {
    id     = "archive-uploads"
    status = "Enabled"

    filter {
      prefix = "uploads/"
    }

    transition {
      days          = var.archive_after_days
      storage_class = "STANDARD_IA"
    }
  }

  rule {
    id     = "archive-corpus"
    status = "Enabled"

    filter {
      prefix = "corpus/"
    }

    transition {
      days          = var.archive_after_days
      storage_class = "GLACIER"
    }
  }

  rule {
    id     = "expire-archive"
    status = var.expire_archive_after_days > 0 ? "Enabled" : "Disabled"

    filter {
      prefix = "archive/"
    }

    expiration {
      days = var.expire_archive_after_days
    }
  }
}

resource "aws_s3_bucket_cors_configuration" "diagram_maker_kb" {
  bucket = aws_s3_bucket.diagram_maker_kb.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST", "HEAD"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

# Bucket policy to allow IAM principals to access the bucket via presigned URLs
# This is required for presigned URLs to work - the bucket policy must allow
# the IAM user/role that generates the presigned URL to perform the operations
resource "aws_s3_bucket_policy" "diagram_maker_kb" {
  bucket = aws_s3_bucket.diagram_maker_kb.id
  depends_on = [aws_s3_bucket_public_access_block.diagram_maker_kb]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowIAMPrincipalsPresignedURLs"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "${aws_s3_bucket.diagram_maker_kb.arn}/*"
      },
      {
        Sid    = "AllowIAMPrincipalsListBucket"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action = [
          "s3:ListBucket"
        ]
        Resource = aws_s3_bucket.diagram_maker_kb.arn
      }
    ]
  })
}

data "aws_caller_identity" "current" {}

