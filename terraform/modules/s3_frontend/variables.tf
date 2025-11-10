variable "bucket_name" {
  type        = string
  description = "Name of the S3 bucket for static website hosting"
}

variable "environment" {
  type        = string
  description = "Environment name (e.g., dev, staging, prod)"
  default     = "dev"
}

variable "index_document" {
  type        = string
  description = "Index document suffix"
  default     = "index.html"
}

variable "error_document" {
  type        = string
  description = "Error document key"
  default     = "404.html"
}

