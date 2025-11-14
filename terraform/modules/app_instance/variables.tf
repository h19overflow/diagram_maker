# Input variable: Environment name
# Used to differentiate resources across environments (dev, staging, prod)
# Appended to resource names to avoid conflicts between environments
variable "environment" {
  type        = string
  description = "Environment name (e.g., dev, staging, prod)"
  default     = "dev"  # Defaults to "dev" if not specified
}

# Input variable: S3 bucket name
# Required variable - must be provided when calling this module
# Used in IAM policies to grant access to the specific S3 bucket
variable "s3_bucket_name" {
  type        = string
  description = "Name of the S3 bucket for knowledge base document storage"
}

# Input variable: EC2 instance name tag
# Used as the "Name" tag on the EC2 instance for easy identification in AWS console
variable "instance_name" {
  type        = string
  description = "Name tag for the EC2 instance"
  default     = "diagram-maker-app"  # Default name if not specified
}

# Input variable: EC2 instance type
# Determines the CPU, RAM, and network performance of the instance
# Common types: t2.micro (free tier), t2.small, t2.medium, t3.large, etc.
variable "instance_type" {
  type        = string
  description = "Instance type for the EC2 instance"
  default     = "t2.small"  # Default to small instance (2 vCPU, 2 GB RAM)
}

# Input variable: SSH Key Pair name (optional)
# If provided, allows SSH access to the instance
# If not provided, use Session Manager (SSM) for browser-based access instead
variable "key_pair_name" {
  type        = string
  description = "Name of the AWS EC2 Key Pair for SSH access (optional - leave empty to use Session Manager)"
  default     = ""
}

# Input variable: ECR repository name
# Used to scope ECR permissions to the specific repository
variable "ecr_repository_name" {
  type        = string
  description = "Name of the ECR repository (e.g., dev-diagram-maker-ecr-repo)"
  default     = ""
}

# Input variable: RDS database resource ID (optional)
# Used for IAM database authentication (more secure than password-based auth)
# If provided, enables the EC2 instance to use IAM authentication for RDS
variable "rds_resource_id" {
  type        = string
  description = "RDS database resource ID for IAM authentication (optional - leave empty to use password-based auth)"
  default     = ""
}

# Input variable: Enable RDS IAM authentication (optional)
# If true, creates IAM policy for database authentication
variable "enable_rds_iam_auth" {
  type        = bool
  description = "Enable IAM database authentication for RDS access"
  default     = false
}