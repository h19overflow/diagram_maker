variable "environment" {
  type        = string
  description = "The environment to deploy the infrastructure to"
  default     = "dev"
}
variable "resource_prefix" {
  type        = string
  description = "The prefix to use for the resource names"
  default     = "dev"
}