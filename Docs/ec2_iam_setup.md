# EC2 Instance and IAM Roles Setup

## Overview

This document describes the EC2 instance infrastructure and IAM roles configuration for the Diagram Maker application. The setup includes secure IAM roles with least-privilege access policies for AWS Bedrock, S3, and CloudWatch services.

## Architecture

The EC2 instance module (`terraform/modules/app_instance`) provisions:
- EC2 instance with Ubuntu 22.04 LTS
- IAM role with necessary permissions
- IAM instance profile attached to EC2
- Security configurations (encryption, monitoring, IMDSv2)

## IAM Roles and Policies

### IAM Role: `diagram-maker-ec2-role-{environment}`

The EC2 instance uses an IAM role that allows it to assume permissions without storing AWS credentials.

**Trust Policy:**
- Allows EC2 service to assume the role
- Uses standard AWS STS assume role policy

### IAM Policies

#### 1. Bedrock Policy (`diagram-maker-bedrock-policy-{environment}`)

**Purpose:** Allows the EC2 instance to invoke AWS Bedrock models for embeddings and LLM inference.

**Permissions:**
- `bedrock:InvokeModel` - Invoke Bedrock foundation models
- `bedrock:InvokeModelWithResponseStream` - Stream responses from Bedrock models

**Allowed Models:**
- `amazon.titan-embed-text-v2:0` - For text embeddings (1024 dimensions)
- `amazon.nova-lite-v1:0` - Lightweight LLM for general tasks
- `amazon.nova-pro-v1:0` - Advanced LLM for complex tasks

**Resource ARNs:**
```
arn:aws:bedrock:ap-southeast-2::foundation-model/amazon.titan-embed-text-v2:0
arn:aws:bedrock:ap-southeast-2::foundation-model/amazon.nova-lite-v1:0
arn:aws:bedrock:ap-southeast-2::foundation-model/amazon.nova-pro-v1:0
```

#### 2. S3 Policy (`diagram-maker-s3-policy-{environment}`)

**Purpose:** Allows the EC2 instance to access the knowledge base S3 bucket for document storage and retrieval.

**Permissions:**
- `s3:GetObject` - Read objects from bucket
- `s3:PutObject` - Upload objects to bucket
- `s3:DeleteObject` - Delete objects from bucket
- `s3:ListBucket` - List bucket contents

**Resources:**
- Bucket: `arn:aws:s3:::{bucket_name}`
- Objects: `arn:aws:s3:::{bucket_name}/*`

**Note:** The bucket name is dynamically passed from the `s3_kb` module output.

#### 3. CloudWatch Logs Policy

**Purpose:** Allows the application to send logs to CloudWatch for monitoring and debugging.

**Policy:** AWS managed policy `CloudWatchLogsFullAccess`

**Permissions Include:**
- Create log groups and streams
- Put log events
- Describe log groups and streams
- Set retention policies

## EC2 Instance Configuration

### Instance Specifications

- **AMI:** Ubuntu 22.04 LTS (Jammy) - Latest HVM SSD
- **Instance Type:** Configurable via `instance_type` variable (default: `t2.medium`)
- **Region:** `ap-southeast-2` (Sydney)

### Security Features

#### 1. IAM Instance Profile
- Attached IAM role via instance profile
- No need for AWS access keys stored on instance
- Credentials automatically rotated by AWS

#### 2. Detailed Monitoring
- CloudWatch detailed monitoring enabled
- 1-minute interval metrics collection
- Enhanced visibility into instance performance

#### 3. EBS Optimization
- EBS-optimized instance enabled
- Improved disk I/O performance
- Reduced latency for EBS volume access

#### 4. IMDSv2 Enforcement
- Instance Metadata Service Version 1 (IMDSv1) disabled
- Only IMDSv2 allowed (requires session tokens)
- Prevents SSRF attacks and unauthorized metadata access

**Configuration:**
```hcl
metadata_options {
  http_endpoint = "enabled"
  http_tokens   = "required"
}
```

#### 5. EBS Volume Encryption
- Root volume encrypted at rest
- Volume type: `gp3` (General Purpose SSD)
- Volume size: 20 GB
- Encryption uses AWS-managed keys

**Configuration:**
```hcl
root_block_device {
  encrypted   = true
  volume_type = "gp3"
  volume_size = 20
}
```

### User Data Script

The instance includes a user data script that:
1. Updates package lists
2. Installs Docker and Docker Compose
3. Starts and enables Docker service
4. Adds `ubuntu` user to docker group

**Note:** The script includes commented instructions for pulling and running the Docker container from ECR. Uncomment and update with your ECR image URI.

## Module Variables

### Required Variables

- `s3_bucket_name` (string) - Name of the S3 bucket for knowledge base document storage

### Optional Variables

- `environment` (string, default: `"dev"`) - Environment name (dev, staging, prod)
- `instance_name` (string, default: `"diagram-maker-app"`) - Name tag for the EC2 instance
- `instance_type` (string, default: `"t2.medium"`) - EC2 instance type

## Module Outputs

- `instance_id` - ID of the EC2 instance
- `instance_public_ip` - Public IP address of the EC2 instance
- `instance_private_ip` - Private IP address of the EC2 instance
- `iam_role_arn` - ARN of the IAM role attached to the EC2 instance
- `iam_instance_profile_name` - Name of the IAM instance profile

## Usage Example

```hcl
module "app_instance" {
  source = "./modules/app_instance"
  
  environment     = var.environment
  s3_bucket_name  = module.s3_kb.bucket_id
  instance_name   = "diagram-maker-app-${var.environment}"
  instance_type   = "t2.medium"  # Optional, defaults to t2.medium
}
```

## Security Best Practices Implemented

1. **Least Privilege Access**
   - IAM policies grant only necessary permissions
   - Bedrock access limited to specific model ARNs
   - S3 access limited to specific bucket

2. **No Hardcoded Credentials**
   - Uses IAM roles instead of access keys
   - Credentials automatically rotated by AWS
   - No secrets stored in user data or configuration

3. **Encryption**
   - EBS volumes encrypted at rest
   - Uses AWS-managed encryption keys

4. **Network Security**
   - IMDSv2 enforced (prevents SSRF attacks)
   - Metadata service access restricted

5. **Monitoring**
   - Detailed CloudWatch monitoring enabled
   - Application logs sent to CloudWatch

## Dependencies

- **S3 KB Module:** Requires S3 bucket to be created first (passed via `s3_bucket_name`)
- **AWS Provider:** Requires AWS provider version ~> 4.0
- **Terraform:** Requires Terraform version >= 1.0

## Troubleshooting

### Instance Cannot Access Bedrock

1. Verify IAM role is attached: Check instance profile in EC2 console
2. Verify Bedrock model access: Ensure models are enabled in Bedrock console
3. Check IAM policy: Verify Bedrock policy is attached to role
4. Check region: Ensure Bedrock is available in `ap-southeast-2`

### Instance Cannot Access S3

1. Verify S3 bucket name: Check `s3_bucket_name` variable matches actual bucket
2. Verify IAM policy: Check S3 policy allows access to correct bucket ARN
3. Check bucket policy: Ensure bucket policy doesn't deny EC2 role
4. Verify region: Ensure bucket is in same region or cross-region access is configured

### Application Logs Not Appearing in CloudWatch

1. Verify CloudWatch policy: Check `CloudWatchLogsFullAccess` is attached
2. Check application configuration: Ensure application is configured to send logs
3. Verify IAM permissions: Check CloudWatch logs permissions in IAM console

## Related Documentation

- [Docker Setup](../DOCKER_RUN.md) - How to build and run the Docker container
- [Terraform Workflow](./terraform_mmd/terraform_workflow.md) - Terraform deployment workflow
- [Infrastructure Architecture](./arch_mmd/infra_architecture.mmd) - High-level infrastructure diagram

