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

