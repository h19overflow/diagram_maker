# RDS Database Module

PostgreSQL database for storing user diagram drafts without authentication.

## Quick Start

### 1. Deploy Infrastructure

```bash
cd terraform

# Initialize Terraform (first time only)
terraform init

# Plan deployment (review changes)
terraform plan -var="db_password=YourSecurePassword123"

# Deploy
terraform apply -var="db_password=YourSecurePassword123"

# Get connection details
terraform output db_instance_endpoint
```

### 2. Initialize Database Schema

After deployment, connect and initialize:

```bash
# Get connection details
DB_HOST=$(terraform output -raw db_instance_address)
DB_PORT=$(terraform output -raw db_instance_port)

# Connect to database
psql -h $DB_HOST -p $DB_PORT -U diagram_maker_admin -d diagram_maker

# Run schema
\i modules/rds_db/schema.sql
```

### 3. Configure Application

Set environment variables:

```env
DB_HOST=<from terraform output db_instance_address>
DB_PORT=5432
DB_NAME=diagram_maker
DB_USER=diagram_maker_admin
DB_PASSWORD=<your-password>
```

## Module Inputs

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `vpc_id` | string | required | VPC ID for RDS deployment |
| `subnet_ids` | list(string) | required | Subnet IDs (min 2, different AZs) |
| `db_password` | string | required | Master password (sensitive) |
| `db_instance_class` | string | `db.t3.micro` | Instance type |
| `multi_az` | bool | `false` | High availability (prod: `true`) |
| `deletion_protection` | bool | `true` | Prevent deletion (prod: `true`) |

See `variables.tf` for full list.

## Module Outputs

| Output | Description |
|--------|-------------|
| `db_instance_endpoint` | Full endpoint (hostname:port) |
| `db_instance_address` | Hostname only |
| `db_connection_string` | Connection string (no password) |
| `db_security_group_id` | Security group ID |

## Security Notes

⚠️ **For Development**:
- Using `allowed_cidr_blocks = ["0.0.0.0/0"]` allows all IPs
- `publicly_accessible = false` keeps it private within VPC
- Password passed via CLI variable

✅ **For Production**:
- Use `allowed_security_groups` instead of CIDR blocks
- Enable `multi_az = true` for high availability
- Enable `deletion_protection = true`
- Set `skip_final_snapshot = false`
- Store password in AWS Secrets Manager
- Enable IAM database authentication

## Database Schema

### Tables

**users** (user_id, created_at, updated_at, user_metadata)
**diagrams** (diagram_id, user_id, s3_path, title, description, user_query, mermaid_code, status, version, created_at, updated_at)

### Indexes

- User-based queries (`idx_diagrams_user_id`)
- Time-based sorting (`idx_diagrams_user_created`)
- Status filtering (`idx_diagrams_user_status`)
- Full-text search (`idx_diagrams_title_search`)

## Cost Estimate (AWS ap-southeast-2)

**Development** (db.t3.micro):
- Instance: ~$15/month
- Storage (20GB): ~$2.30/month
- Backup (7 days): ~$1/month
- **Total: ~$18-20/month**

**Production** (db.t3.small + Multi-AZ):
- Instance: ~$60/month
- Storage (100GB): ~$11.50/month
- Backup: ~$5/month
- **Total: ~$75-80/month**

## Troubleshooting

**Connection timeout**:
- Check security group allows traffic from EC2
- Verify subnets are in correct VPC
- Check RDS is in `available` state

**Authentication failed**:
- Verify password is correct
- Check username matches `db_username` variable
- For IAM auth: verify IAM policy attached to EC2 role

**Schema initialization fails**:
- Ensure database exists (created automatically on first deployment)
- Check UUID extension is available: `CREATE EXTENSION IF NOT EXISTS "uuid-ossp";`
