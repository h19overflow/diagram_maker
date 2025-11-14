# RDS Database Module

PostgreSQL database for storing user diagram drafts without authentication.

## Quick Start

### 1. Deploy Infrastructure

```bash
cd terraform

# Initialize Terraform (first time only)
terraform init

# Plan deployment (review changes)
terraform plan -var="db_password=postgres"

# Deploy
terraform apply -var="db_password=postgres"

# Get connection details
terraform output db_instance_endpoint
```

### 2. Initialize Database Schema

After deployment, connect and initialize:

**For Bash/Linux/Mac:**
```bash
# Get connection details
DB_HOST=$(terraform output -raw db_instance_address)
DB_PORT=$(terraform output -raw db_instance_port)

# Connect to database (password: postgres)
psql -h $DB_HOST -p $DB_PORT -U diagram_maker_admin -d diagram_maker

# Run schema
\i modules/rds_db/schema.sql
```

**For PowerShell (Windows):**
```powershell
# Get connection details
$DB_HOST = terraform output -raw db_instance_address
$DB_PORT = terraform output -raw db_instance_port

# Connect to database (password: postgres)
psql -h $DB_HOST -p $DB_PORT -U diagram_maker_admin -d diagram_maker

# Run schema
\i schema.sql
```

### 3. Configure Application

Set environment variables:

```env
DB_HOST=<from terraform output db_instance_address>
DB_PORT=5432
DB_NAME=diagram_maker
DB_USER=diagram_maker_admin
DB_PASSWORD=postgres
```

## Module Inputs

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `vpc_id` | string | required | VPC ID for RDS deployment |
| `subnet_ids` | list(string) | required | Subnet IDs (min 2, different AZs) |
| `db_password` | string | required | Master password (default: `postgres` for dev) |
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
- Default password: `postgres` (⚠️ **CHANGE FOR PRODUCTION**)
- Password passed via CLI variable: `terraform apply -var="db_password=postgres"`

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

**Connection timeout from local machine**:
- ⚠️ **RDS is private** (`publicly_accessible = false`) - it can only be accessed from within the VPC
- You cannot connect directly from your local machine
- **Solutions:**
  1. **Connect through EC2 instance** (recommended):
     - SSH into your EC2 instance in the same VPC
     - Connect to RDS from the EC2 instance using the private endpoint
  2. **Use SSH tunnel** (if EC2 has SSH access):
     ```bash
     ssh -L 5432:RDS_ENDPOINT:5432 user@EC2_INSTANCE_IP
     # Then connect to localhost:5432 from your local machine
     ```
  3. **Use AWS Session Manager port forwarding**:
     ```bash
     aws ssm start-session --target EC2_INSTANCE_ID --document-name AWS-StartPortForwardingSession --parameters '{"portNumber":["5432"],"localPortNumber":["5432"]}'
     ```
  4. **Temporarily enable public access** (dev only, not recommended):
     - Set `publicly_accessible = true` in terraform.tfvars
     - Add your public IP to `allowed_cidr_blocks`
     - Run `terraform apply` to update

**Connection timeout from EC2**:
- Check security group allows traffic from EC2 security group
- Verify subnets are in correct VPC
- Check RDS is in `available` state
- Verify EC2 and RDS are in the same VPC

**Authentication failed**:
- Verify password is correct
- Check username matches `db_username` variable
- For IAM auth: verify IAM policy attached to EC2 role

**Schema initialization fails**:
- Ensure database exists (created automatically on first deployment)
- Check UUID extension is available: `CREATE EXTENSION IF NOT EXISTS "uuid-ossp";`

## Enhanced Monitoring

### What is Enhanced Monitoring?

Enhanced Monitoring provides detailed, real-time metrics about your RDS instance at the operating system level, with metrics available every 1-60 seconds (configurable).

### Standard vs Enhanced Monitoring

**Standard CloudWatch Monitoring (Default):**
- ✅ Metrics every 5 minutes
- ✅ Basic metrics: CPU, memory, storage, network
- ✅ Free (included with RDS)
- ✅ No IAM role required
- ✅ Sufficient for most development workloads

**Enhanced Monitoring:**
- ✅ Metrics every 1, 5, 10, 15, 30, or 60 seconds (configurable)
- ✅ Detailed OS-level metrics:
  - CPU utilization per core
  - Memory (RAM, cache, swap)
  - Disk I/O (read/write operations, queue depth)
  - Network (packets, throughput)
  - Process/thread counts
  - Database connections
- ✅ Free (no additional cost, uses CloudWatch Logs)
- ⚠️ Requires IAM role (RDS can create it automatically or you provide one)

### When to Use Enhanced Monitoring

**Use Enhanced Monitoring for:**
- Production environments requiring detailed performance insights
- Troubleshooting performance bottlenecks
- Fine-tuning database configuration
- Debugging slow queries or resource constraints
- Real-time monitoring of critical databases

**Skip Enhanced Monitoring for:**
- Development/test environments
- Low-traffic applications
- When basic CloudWatch metrics are sufficient

### Configuration

Enhanced monitoring is **disabled by default** in this module. To enable:

1. **Option 1: Let RDS create the monitoring role automatically**
   - Set `monitoring_role_arn = ""` (empty) and `monitoring_interval = 60`
   - RDS will create the role automatically

2. **Option 2: Provide your own IAM role**
   - Create an IAM role with the `rds-monitoring-role` trust policy
   - Set `monitoring_role_arn` to the role ARN
   - Set `monitoring_interval` to desired interval (60 seconds recommended)

**Current Configuration:**
- Enhanced monitoring is **disabled** (`monitoring_interval = 0`) when no role is provided
- CloudWatch logs are still enabled for basic monitoring
- This is the recommended setup for development environments
