terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

# Create KMS key for ECR encryption
resource "aws_kms_key" "ecr_encryption" {
  description             = "KMS key for ECR repository encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow ECR to use the key"
        Effect = "Allow"
        Principal = {
          Service = "ecr.amazonaws.com"
        }
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Environment = var.environment
    Project     = "${var.resource_prefix}-diagram-maker"
    Resource    = "ecr-kms"
  }
}

data "aws_caller_identity" "current" {}

resource "aws_kms_alias" "ecr_encryption" {
  name          = "alias/${var.resource_prefix}-diagram-maker-ecr"
  target_key_id = aws_kms_key.ecr_encryption.key_id
}

# checkov:skip=CKV_AWS_52:MUTABLE tags required for development workflow
resource "aws_ecr_repository" "diagram_maker_ecr_repo" {
  name                 = "${var.resource_prefix}-diagram-maker-ecr-repo"
  image_tag_mutability = "MUTABLE"

  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = aws_kms_key.ecr_encryption.arn
  }

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Environment = var.environment
    Project     = "${var.resource_prefix}-diagram-maker"
    Resource    = "ecr"
  }
}