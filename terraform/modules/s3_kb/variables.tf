variable "bucket_name" {
  type        = string
  description = "Name of the S3 bucket for knowledge base document storage"
}

variable "environment" {
  type        = string
  description = "Environment name (e.g., dev, staging, prod)"
  default     = "dev"
}

variable "enable_lifecycle_rules" {
  type        = bool
  description = "Enable lifecycle rules for automatic archiving"
  default     = true
}

variable "archive_after_days" {
  type        = number
  description = "Number of days before moving objects to archive prefix"
  default     = 90
}

variable "expire_archive_after_days" {
  type        = number
  description = "Number of days before deleting archived objects (0 to disable)"
  default     = 365
}

