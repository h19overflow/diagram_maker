variable "environment" {
    type = string
    description = "The environment to deploy the infrastructure to"
    default = "dev"
}
variable "resource_prefix" {
    type = string
    description = "The prefix to use for the resource names"
    default = "dev"
}

# RDS Database Password
# IMPORTANT: In production, use AWS Secrets Manager instead of passing this as a variable
# For dev: terraform apply -var="db_password=YourSecurePassword123"
variable "db_password" {
    type        = string
    description = "Master password for the RDS database (minimum 8 characters)"
    sensitive   = true
    default     = ""  # Must be provided via -var or terraform.tfvars
}