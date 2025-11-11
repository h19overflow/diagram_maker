terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region  = "ap-southeast-2"
  profile = "default"
}

data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical
}

# IAM Role for EC2 instance
resource "aws_iam_role" "ec2_role" {
  name = "diagram-maker-ec2-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "diagram-maker-ec2-role-${var.environment}"
    Environment = var.environment
  }
}

# IAM Policy for Bedrock access
resource "aws_iam_policy" "bedrock_policy" {
  name        = "diagram-maker-bedrock-policy-${var.environment}"
  description = "Policy for Bedrock access (embeddings and LLM)"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = [
          "arn:aws:bedrock:ap-southeast-2::foundation-model/amazon.titan-embed-text-v2:0",
          "arn:aws:bedrock:ap-southeast-2::foundation-model/amazon.nova-lite-v1:0",
          "arn:aws:bedrock:ap-southeast-2::foundation-model/amazon.nova-pro-v1:0"
        ]
      }
    ]
  })

  tags = {
    Name        = "diagram-maker-bedrock-policy-${var.environment}"
    Environment = var.environment
  }
}

# IAM Policy for S3 access
resource "aws_iam_policy" "s3_policy" {
  name        = "diagram-maker-s3-policy-${var.environment}"
  description = "Policy for S3 bucket access"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.s3_bucket_name}",
          "arn:aws:s3:::${var.s3_bucket_name}/*"
        ]
      }
    ]
  })

  tags = {
    Name        = "diagram-maker-s3-policy-${var.environment}"
    Environment = var.environment
  }
}

# Attach Bedrock policy to role
resource "aws_iam_role_policy_attachment" "bedrock_attachment" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.bedrock_policy.arn
}

# Attach S3 policy to role
resource "aws_iam_role_policy_attachment" "s3_attachment" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.s3_policy.arn
}

# Attach CloudWatch Logs policy (for application logging)
resource "aws_iam_role_policy_attachment" "cloudwatch_logs_attachment" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}

# Instance Profile for EC2
resource "aws_iam_instance_profile" "ec2_profile" {
  name = "diagram-maker-ec2-profile-${var.environment}"
  role = aws_iam_role.ec2_role.name

  tags = {
    Name        = "diagram-maker-ec2-profile-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_instance" "example" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type

  # Attach IAM instance profile
  iam_instance_profile = aws_iam_instance_profile.ec2_profile.name

  # Enable detailed monitoring
  monitoring = true

  # Enable EBS optimization (required for t2.medium and above)
  ebs_optimized = true

  # Disable IMDSv1, enable IMDSv2 only
  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  # Root volume with encryption
  root_block_device {
    encrypted   = true
    volume_type = "gp3"
    volume_size = 20
  }

  # User data script to install Docker and run container
  user_data = <<-EOF
              #!/bin/bash
              apt-get update
              apt-get install -y docker.io docker-compose
              systemctl start docker
              systemctl enable docker
              usermod -aG docker ubuntu
              
              # Pull and run the Docker container
              # Note: Replace with your ECR image URI
              # docker pull <your-ecr-uri>/diagram-maker:latest
              # docker run -d --name diagram-maker -p 8001:8001 <your-ecr-uri>/diagram-maker:latest
              EOF

  tags = {
    Name        = var.instance_name
    Environment = var.environment
  }
}