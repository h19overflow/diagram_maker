module "s3_frontend" {
  source = "./modules/s3_frontend"
  
  bucket_name    = "diagram-maker-frontend-${var.environment}"
  environment    = var.environment
  index_document = "index.html"
  error_document = "404.html"
}

module "s3_kb" {
  source = "./modules/s3_kb"
  
  bucket_name              = "diagram-maker-kb-${var.environment}"
  environment              = var.environment
  enable_lifecycle_rules   = true
  archive_after_days       = 90
  expire_archive_after_days = 365
}

module "ecr" {
  source = "./modules/ecr"
  environment = var.environment
  resource_prefix = var.resource_prefix
}

module "app_instance" {
  source = "./modules/app_instance"
  environment     = var.environment
  s3_bucket_name  = module.s3_kb.bucket_id
  instance_name   = "diagram-maker-app-${var.environment}"
}