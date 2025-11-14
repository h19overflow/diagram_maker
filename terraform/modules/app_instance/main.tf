# Terraform configuration block - defines version requirements and providers
terraform {
  required_version = ">= 1.0"

  # Specify which providers are needed and their versions
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"  # Use AWS provider version 4.x
    }
  }
}

# AWS provider configuration - tells Terraform which AWS account/region to use
provider "aws" {
  region  = "ap-southeast-2"  # Sydney, Australia region
  profile = "default"         # Use default AWS credentials profile
}

# Data source to find the latest Ubuntu 22.04 AMI (Amazon Machine Image)
# This dynamically looks up the AMI ID instead of hardcoding it
data "aws_ami" "ubuntu" {
  most_recent = true  # Get the most recent version available

  # Filter by AMI name pattern - Ubuntu 22.04 Jammy Jellyfish
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  # Filter by virtualization type - HVM (Hardware Virtual Machine) required for modern instances
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical's AWS account ID (official Ubuntu publisher)
}

# Data source to get current AWS account ID
# Used to construct ECR repository ARNs for IAM policies
data "aws_caller_identity" "current" {}

resource "aws_iam_role" "ec2_role" {
  name = "diagram-maker-ec2-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"  # Security Token Service action to assume role
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"  # Only EC2 service can use this role
        }
      }
    ]
  })

  tags = {
    Name        = "diagram-maker-ec2-role-${var.environment}"
    Environment = var.environment
  }
}


resource "aws_iam_policy" "bedrock_policy" {
  name        = "diagram-maker-bedrock-policy-${var.environment}"
  description = "Policy for Bedrock access (embeddings and LLM)"

  # The actual permissions document
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        # Actions allowed: invoke models (synchronous) and stream responses
        Action = [
          "bedrock:InvokeModel",                    # Standard model invocation
          "bedrock:InvokeModelWithResponseStream"   # Streaming responses for better UX
        ]
        # Specific model ARNs that can be invoked (scoped to ap-southeast-2 region)
        Resource = [
          "arn:aws:bedrock:ap-southeast-2::foundation-model/amazon.titan-embed-text-v2:0",  # Embedding model
          "arn:aws:bedrock:ap-southeast-2::foundation-model/amazon.nova-lite-v1:0",         # Lightweight LLM
          "arn:aws:bedrock:ap-southeast-2::foundation-model/amazon.nova-pro-v1:0"           # More capable LLM
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
# Allows the EC2 instance to read/write files in the S3 bucket
# Used for storing knowledge base documents and other application data
resource "aws_iam_policy" "s3_policy" {
  name        = "diagram-maker-s3-policy-${var.environment}"
  description = "Policy for S3 bucket access"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        # S3 actions allowed: read objects, write objects, delete objects, list bucket contents
        Action = [
          "s3:GetObject",     # Download files from S3
          "s3:PutObject",     # Upload files to S3
          "s3:DeleteObject",  # Delete files from S3
          "s3:ListBucket"     # List files in the bucket (required to browse bucket)
        ]
        # Resource ARNs: bucket itself and all objects within it
        Resource = [
          "arn:aws:s3:::${var.s3_bucket_name}",      # Bucket-level permissions (for ListBucket)
          "arn:aws:s3:::${var.s3_bucket_name}/*"     # Object-level permissions (for Get/Put/Delete)
        ]
      }
    ]
  })

  tags = {
    Name        = "diagram-maker-s3-policy-${var.environment}"
    Environment = var.environment
  }
}


resource "aws_iam_policy" "ecr_policy" {
  name        = "diagram-maker-ecr-policy-${var.environment}"
  description = "Policy for ECR access to pull Docker images"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ECRGetAuthorizationToken"
        Effect = "Allow"
        # GetAuthorizationToken must use "*" - it's an account-level action
        Action   = "ecr:GetAuthorizationToken"
        Resource = "*"
      },
      {
        Sid    = "ECRPullImages"
        Effect = "Allow"
        # Scoped ECR actions for specific repository
        Action = [
          "ecr:BatchCheckLayerAvailability",  # Check if image layers exist
          "ecr:GetDownloadUrlForLayer",       # Get download URLs for image layers
          "ecr:BatchGetImage"                  # Download the actual image
        ]
        # Scope to specific ECR repository if provided, otherwise allow all repos
        Resource = var.ecr_repository_name != "" ? [
          "arn:aws:ecr:ap-southeast-2:${data.aws_caller_identity.current.account_id}:repository/${var.ecr_repository_name}"
        ] : ["arn:aws:ecr:ap-southeast-2:${data.aws_caller_identity.current.account_id}:repository/*"]
      }
    ]
  })

  tags = {
    Name        = "diagram-maker-ecr-policy-${var.environment}"
    Environment = var.environment
  }
}

# Attach Bedrock policy to role
# Links the Bedrock permissions policy to the EC2 role
# This gives the EC2 instance permission to call Bedrock models
resource "aws_iam_role_policy_attachment" "bedrock_attachment" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.bedrock_policy.arn
}

# Attach S3 policy to role
# Links the S3 permissions policy to the EC2 role
# This gives the EC2 instance permission to access the S3 bucket
resource "aws_iam_role_policy_attachment" "s3_attachment" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.s3_policy.arn
}

# Attach CloudWatch Logs policy (for application logging)
# Uses AWS managed policy for CloudWatch Logs access
# Allows the application to write logs to CloudWatch for monitoring and debugging
resource "aws_iam_role_policy_attachment" "cloudwatch_logs_attachment" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"  # AWS managed policy
}

# Attach ECR policy to role
# Links the ECR permissions policy to the EC2 role
# This gives the EC2 instance permission to pull Docker images from ECR
resource "aws_iam_role_policy_attachment" "ecr_attachment" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.ecr_policy.arn
}

# IAM Policy for RDS access (optional - for IAM database authentication)
# Allows the EC2 instance to connect to RDS using IAM authentication (no passwords)
# More secure than password-based authentication, uses temporary credentials
resource "aws_iam_policy" "rds_policy" {
  count       = var.enable_rds_iam_auth ? 1 : 0
  name        = "diagram-maker-rds-policy-${var.environment}"
  description = "Policy for RDS IAM database authentication"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        # Action to connect to RDS using IAM authentication
        Action = [
          "rds-db:connect"
        ]
        # Resource: specific RDS instance (uses resource ID)
        # Format: arn:aws:rds-db:<region>:<account-id>:dbuser:<resource-id>/<db-username>
        Resource = [
          "arn:aws:rds-db:ap-southeast-2:${data.aws_caller_identity.current.account_id}:dbuser:${var.rds_resource_id}/*"
        ]
      }
    ]
  })

  tags = {
    Name        = "diagram-maker-rds-policy-${var.environment}"
    Environment = var.environment
  }
}

# Attach RDS policy to role (only if IAM auth is enabled)
# Links the RDS permissions policy to the EC2 role
# This gives the EC2 instance permission to use IAM authentication for RDS
resource "aws_iam_role_policy_attachment" "rds_attachment" {
  count      = var.enable_rds_iam_auth ? 1 : 0
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.rds_policy[0].arn
}

# Attach SSM (Session Manager) policy to role
# Allows browser-based access to EC2 instance via AWS Systems Manager Session Manager
# This enables secure access without SSH keys or open ports
# You can connect via: AWS Console → EC2 → Connect → Session Manager
resource "aws_iam_role_policy_attachment" "ssm_attachment" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"  # AWS managed policy for SSM
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "diagram-maker-ec2-profile-${var.environment}"
  role = aws_iam_role.ec2_role.name  # Reference to the IAM role created above

  tags = {
    Name        = "diagram-maker-ec2-profile-${var.environment}"
    Environment = var.environment
  }
}

# EC2 Instance - The actual virtual server that will run the application
resource "aws_instance" "diagram_maker_app" {
  ami           = data.aws_ami.ubuntu.id  # Use the Ubuntu AMI found by the data source
  instance_type = var.instance_type       # Instance size (CPU/RAM) - defaults to t2.small

  # Attach IAM instance profile
  # This gives the instance access to AWS services (Bedrock, S3, CloudWatch) via the IAM role
  iam_instance_profile = aws_iam_instance_profile.ec2_profile.name

  # SSH Key Pair (optional)
  # If provided, allows SSH access. If empty, use Session Manager (SSM) instead
  # Session Manager is recommended - works through browser, no keys needed, more secure
  key_name = var.key_pair_name != "" ? var.key_pair_name : null

  # Enable detailed monitoring
  # Provides 1-minute CloudWatch metrics instead of default 5-minute intervals
  monitoring = true

  # Enable EBS optimization (required for t2.medium and above)
  # Dedicates network bandwidth for EBS volume traffic, improving disk I/O performance
  ebs_optimized = true

  # Disable IMDSv1, enable IMDSv2 only
  # IMDS (Instance Metadata Service) provides instance info and temporary credentials
  # IMDSv2 requires a token, making it more secure against SSRF attacks
  metadata_options {
    http_endpoint = "enabled"   # Enable metadata service
    http_tokens   = "required"  # Require IMDSv2 tokens (more secure)
  }

  # Root volume with encryption
  # The boot disk for the EC2 instance
  root_block_device {
    encrypted   = true      # Encrypt the disk at rest for security
    volume_type = "gp3"     # General Purpose SSD (gp3) - latest generation, better performance
    volume_size = 20        # 20 GB disk space
  }

  # User data script to install Docker and run container
  # This bash script runs once when the instance first boots up
  # It installs Docker and prepares the environment to run the application container
  user_data = <<-EOF
              #!/bin/bash
              set -e  # Exit on any error

              # Update package lists and install required packages
              apt-get update
              apt-get install -y docker.io docker-compose awscli

              # Ensure SSM Agent is running for Session Manager (browser-based access)
              # Ubuntu 22.04 AMI includes SSM agent pre-installed, just ensure it's running
              # This allows connecting to the instance via AWS Console without SSH keys
              # If agent not installed, install it (fallback for older AMIs)
              if ! command -v amazon-ssm-agent &> /dev/null; then
                mkdir -p /tmp/ssm
                cd /tmp/ssm
                wget https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/debian_amd64/amazon-ssm-agent.deb
                dpkg -i amazon-ssm-agent.deb || true
              fi
              systemctl enable amazon-ssm-agent || true
              systemctl start amazon-ssm-agent || true

              # Start Docker service
              systemctl start docker
              systemctl enable docker
              
              # Add ubuntu user to docker group (allows running docker without sudo)
              # Note: User must log out/in or use 'newgrp docker' for group membership to take effect
              usermod -aG docker ubuntu
              
              # Wait a moment for Docker to be fully ready
              sleep 5

              # Authenticate Docker with ECR (required before pulling images)
              # The IAM role attached to this instance provides credentials automatically
              # Using sudo here since we're in user_data script context
              aws ecr get-login-password --region ap-southeast-2 | sudo docker login --username AWS --password-stdin 575734508049.dkr.ecr.ap-southeast-2.amazonaws.com

              # Pull and run the Docker container
              # ECR URI format: <account-id>.dkr.ecr.<region>.amazonaws.com/<repository-name>:<tag>
              ECR_URI="575734508049.dkr.ecr.ap-southeast-2.amazonaws.com/dev-diagram-maker-ecr-repo:latest"
              sudo docker pull $ECR_URI
              sudo docker run -d --name diagram-maker -p 8001:8001 --restart unless-stopped $ECR_URI
              
              # Create a helper script for ubuntu user to use docker without sudo
              # This activates the docker group membership in the current shell
              echo '#!/bin/bash' > /home/ubuntu/use-docker.sh
              echo 'newgrp docker << EOF' >> /home/ubuntu/use-docker.sh
              echo 'docker "$@"' >> /home/ubuntu/use-docker.sh
              echo 'EOF' >> /home/ubuntu/use-docker.sh
              chmod +x /home/ubuntu/use-docker.sh
              chown ubuntu:ubuntu /home/ubuntu/use-docker.sh
              EOF

  tags = {
    Name        = var.instance_name
    Environment = var.environment
  }
}