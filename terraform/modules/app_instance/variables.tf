variable "environment" {
  type        = string
  description = "Environment name (e.g., dev, staging, prod)"
  default     = "dev"
}

variable "s3_bucket_name" {
  type        = string
  description = "Name of the S3 bucket for knowledge base document storage"
}

variable "instance_name" {
  type        = string
  description = "Name tag for the EC2 instance"
  default     = "diagram-maker-app"
}

variable "instance_type" {
  type        = string
  description = "Instance type for the EC2 instance"
  default     = "t2.medium"
}