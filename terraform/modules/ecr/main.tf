terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

# checkov:skip=CKV_AWS_52:MUTABLE tags required for development workflow
resource "aws_ecr_repository" "diagram_maker_ecr_repo" {
  name                 = "${var.resource_prefix}-diagram-maker-ecr-repo"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Environment = var.environment
    Project     = "${var.resource_prefix}-diagram-maker"
    Resource    = "ecr"
  }
}