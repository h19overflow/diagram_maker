# Terraform Module Workflow Guide

This guide explains the step-by-step process of creating reusable Terraform modules and using them in your infrastructure.

## Overview

Terraform modules allow you to package infrastructure components into reusable units. This guide walks through the complete workflow from creating variables to exposing outputs.

---

## Step 1: Define Variables (Avoid Hardcoding)

**Location:** `terraform/modules/<module_name>/variables.tf`

Variables make your modules flexible and reusable. Never hardcode values that might change between environments or deployments.

### Example: S3 Frontend Module Variables

```terraform
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
```

### Why Variables Matter

- **Reusability:** Same module works for dev, staging, and prod
- **Flexibility:** Easy to change values without editing resource blocks
- **Maintainability:** Clear documentation of what each value does
- **Type Safety:** Terraform validates types (string, number, bool, etc.)

### Variable Types

- `string` - Text values
- `number` - Numeric values
- `bool` - true/false
- `list` - Arrays like `["item1", "item2"]`
- `map` - Key-value pairs
- `object` - Complex structures

---

## Step 2: Each Resource Has Its Own Configuration Resources

**Location:** `terraform/modules/<module_name>/main.tf`

In AWS (and most cloud providers), a single resource often requires multiple separate configuration resources. Each configuration is a separate Terraform resource block.

### Example: S3 Bucket Configuration

Creating an S3 bucket with all its features requires multiple resources:

```terraform
# 1. The main bucket resource
resource "aws_s3_bucket" "static_site" {
  bucket = var.bucket_name
}

# 2. Versioning configuration (separate resource)
resource "aws_s3_bucket_versioning" "static_site" {
  bucket = aws_s3_bucket.static_site.id
  versioning_configuration {
    status = "Enabled"
  }
}

# 3. Encryption configuration (separate resource)
resource "aws_s3_bucket_server_side_encryption_configuration" "static_site" {
  bucket = aws_s3_bucket.static_site.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# 4. Public access block (separate resource)
resource "aws_s3_bucket_public_access_block" "static_site" {
  bucket = aws_s3_bucket.static_site.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# 5. Website configuration (separate resource)
resource "aws_s3_bucket_website_configuration" "static_site" {
  bucket = aws_s3_bucket.static_site.id
  index_document {
    suffix = var.index_document
  }
  error_document {
    key = var.error_document
  }
}
```

### Key Points

- **One resource type = One configuration concern**
- Each resource references the main bucket using `aws_s3_bucket.static_site.id`
- Resources are linked through references, not nested blocks
- Terraform automatically determines creation order based on dependencies

### Resource Naming Pattern

```
resource "aws_s3_bucket" "local_name" { }
resource "aws_s3_bucket_<feature>" "local_name" {
  bucket = aws_s3_bucket.local_name.id
}
```

The `local_name` stays consistent to show they're related.

---

## Step 3: Define Outputs at Module Level

**Location:** `terraform/modules/<module_name>/outputs.tf`

Module outputs expose important values from the module so they can be used elsewhere. Think of them as the module's "public API."

### Example: S3 Frontend Module Outputs

```terraform
output "bucket_id" {
  description = "ID of the S3 bucket"
  value       = aws_s3_bucket.static_site.id
}

output "bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.static_site.arn
}

output "website_endpoint" {
  description = "Website endpoint URL"
  value       = aws_s3_bucket_website_configuration.static_site.website_endpoint
}

output "website_domain" {
  description = "Website domain"
  value       = aws_s3_bucket_website_configuration.static_site.website_domain
}
```

### Why Module-Level Outputs?

- **Encapsulation:** Module consumers don't need to know internal resource names
- **Abstraction:** Hide complexity - expose only what's needed
- **Reusability:** Other modules or root can reference these values
- **Documentation:** Clear description of what each output provides

### Output Syntax

```terraform
output "output_name" {
  description = "What this output represents"
  value       = resource_type.resource_name.attribute
}
```

---

## Step 4: Define Modules in Main Configuration

**Location:** `terraform/main.tf`

The root `main.tf` file is where you actually **use** your modules. This is where modules are instantiated with specific values.

### Example: Using S3 Modules

```terraform
module "s3_frontend" {
  source = "./modules/s3_frontend"
  
  bucket_name    = "hadith-scholar-frontend-${var.environment}"
  environment    = var.environment
  index_document = "index.html"
  error_document = "404.html"
}

module "s3_kb" {
  source = "./modules/s3_kb"
  
  bucket_name              = "hadith-scholar-kb-${var.environment}"
  environment              = var.environment
  enable_lifecycle_rules   = true
  archive_after_days       = 90
  expire_archive_after_days = 365
}
```

### Module Block Syntax

```terraform
module "local_module_name" {
  source = "./modules/module_directory"
  
  variable_name = "value"
  another_var  = var.root_variable
}
```

### Key Points

- **`source`** - Path to the module directory
- **`local_module_name`** - How you reference this module instance (used in outputs)
- **Variable assignments** - Pass values to module variables
- **Multiple instances** - You can call the same module multiple times with different names

### Example: Multiple Environments

```terraform
module "s3_frontend_dev" {
  source = "./modules/s3_frontend"
  bucket_name = "my-app-frontend-dev"
  environment = "dev"
}

module "s3_frontend_prod" {
  source = "./modules/s3_frontend"
  bucket_name = "my-app-frontend-prod"
  environment = "prod"
}
```

---

## Step 5: Define Outputs in Root Outputs File (Optional Re-exposure)

**Location:** `terraform/outputs.tf`

You can (and often should) re-expose module outputs at the root level. This creates a single place to see all important infrastructure values.

### Example: Root-Level Outputs

```terraform
# Re-expose module outputs with descriptive names
output "frontend_bucket_id" {
  description = "Frontend S3 bucket ID"
  value       = module.s3_frontend.bucket_id
}

output "frontend_website_endpoint" {
  description = "Frontend website endpoint URL"
  value       = module.s3_frontend.website_endpoint
}

output "kb_bucket_id" {
  description = "Knowledge base S3 bucket ID"
  value       = module.s3_kb.bucket_id
}

output "kb_uploads_prefix" {
  description = "Prefix path for uploads"
  value       = module.s3_kb.uploads_prefix
}
```

### Why Define Outputs Twice?

1. **Centralized View:** All infrastructure outputs in one place
2. **Better Naming:** Root outputs can have more descriptive names
3. **Abstraction:** Consumers don't need to know module structure
4. **Documentation:** Single source of truth for what's available
5. **Integration:** Easier to pass to other tools or scripts

### Output Reference Syntax

```terraform
# Reference module output
module.<module_name>.<output_name>

# Example
module.s3_frontend.bucket_id
module.s3_kb.uploads_prefix
```

---

## Complete Workflow Summary

```
1. Define Variables (variables.tf)
   ↓
2. Create Resources (main.tf)
   - Main resource
   - Configuration resources
   - Reference main resource
   ↓
3. Define Module Outputs (outputs.tf)
   - Expose important values
   ↓
4. Use Module in Root (main.tf)
   - Call module with source
   - Pass variable values
   ↓
5. Re-expose in Root Outputs (outputs.tf)
   - Reference module outputs
   - Provide centralized view
```

---

## Real-World Example: Complete Flow

### Module Structure
```
terraform/modules/s3_frontend/
├── variables.tf    (Step 1: Define variables)
├── main.tf         (Step 2: Create resources)
└── outputs.tf     (Step 3: Module outputs)
```

### Root Structure
```
terraform/
├── variables.tf    (Root-level variables)
├── main.tf         (Step 4: Use modules)
├── outputs.tf      (Step 5: Re-expose outputs)
└── provider.tf     (Provider configuration)
```

### Execution Flow

1. **Terraform reads `main.tf`** → Finds module calls
2. **Terraform reads module `variables.tf`** → Knows what inputs are needed
3. **Terraform reads module `main.tf`** → Creates all resources
4. **Terraform reads module `outputs.tf`** → Exposes module outputs
5. **Terraform reads root `outputs.tf`** → Re-exposes selected outputs

---

## Best Practices

1. **Always use variables** - Never hardcode environment-specific values
2. **One concern per resource** - Each configuration gets its own resource block
3. **Document outputs** - Always include descriptions
4. **Consistent naming** - Use same local names for related resources
5. **Re-expose important outputs** - Make root outputs the single source of truth
6. **Use defaults wisely** - Provide sensible defaults but allow overrides

---

## Common Patterns

### Pattern 1: Environment-Based Naming
```terraform
bucket_name = "my-app-${var.environment}"
```

### Pattern 2: Conditional Resources
```terraform
resource "aws_s3_bucket_lifecycle_configuration" "kb_docs" {
  count  = var.enable_lifecycle_rules ? 1 : 0
  bucket = aws_s3_bucket.kb_docs.id
  # ...
}
```

### Pattern 3: String Interpolation
```terraform
Resource = "${aws_s3_bucket.static_site.arn}/*"
```

### Pattern 4: Dependencies
```terraform
depends_on = [aws_s3_bucket_public_access_block.static_site]
```

---

## Quick Reference

| Step | File | Purpose |
|------|------|---------|
| 1 | `modules/*/variables.tf` | Define inputs |
| 2 | `modules/*/main.tf` | Create resources |
| 3 | `modules/*/outputs.tf` | Expose module values |
| 4 | `main.tf` | Use modules |
| 5 | `outputs.tf` | Re-expose outputs |

---

## Next Steps

- Run `terraform init` to download providers and initialize modules
- Run `terraform plan` to see what will be created
- Run `terraform apply` to create the infrastructure
- Use `terraform output` to view output values

