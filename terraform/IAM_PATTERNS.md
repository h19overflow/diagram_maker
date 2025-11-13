# AWS IAM Role Patterns Across Services

This document explains how IAM roles work differently across various AWS services, with Terraform examples.

## Common Pattern (All Services)

The fundamental pattern is consistent:
1. **Create Role** (`aws_iam_role`) - Defines who can assume it via `assume_role_policy`
2. **Create Policies** (`aws_iam_policy`) - Define what permissions are allowed
3. **Attach Policies to Role** (`aws_iam_role_policy_attachment`) - Link permissions to role
4. **Attach Role to Resource** - Method varies by service

---

## Pattern 1: EC2 Instances (Requires Instance Profile)

**Flow:** Role → Policies → Attach Policies → **Instance Profile** → Attach to EC2

EC2 is unique - it requires an Instance Profile wrapper because EC2 instances run your own OS.

### Example: EC2 with Bedrock, S3, ECR Access

```terraform
# Step 1: Create IAM Role with trust policy
resource "aws_iam_role" "ec2_role" {
  name = "my-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"  # Only EC2 can assume this
      }
    }]
  })
}

# Step 2: Create Policies (permission documents)
resource "aws_iam_policy" "s3_policy" {
  name = "s3-access-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["s3:GetObject", "s3:PutObject"]
      Resource = "arn:aws:s3:::my-bucket/*"
    }]
  })
}

resource "aws_iam_policy" "bedrock_policy" {
  name = "bedrock-access-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["bedrock:InvokeModel"]
      Resource = "arn:aws:bedrock:*::foundation-model/*"
    }]
  })
}

# Step 3: Attach Policies to Role
resource "aws_iam_role_policy_attachment" "s3_attachment" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.s3_policy.arn
}

resource "aws_iam_role_policy_attachment" "bedrock_attachment" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.bedrock_policy.arn
}

# Step 4: Create Instance Profile (EC2-specific wrapper)
resource "aws_iam_instance_profile" "ec2_profile" {
  name = "my-ec2-profile"
  role = aws_iam_role.ec2_role.name  # Wrap the role
}

# Step 5: Attach Profile to EC2 Instance
resource "aws_instance" "my_app" {
  ami           = "ami-12345"
  instance_type = "t2.small"
  
  # EC2 uses instance_profile, not role directly
  iam_instance_profile = aws_iam_instance_profile.ec2_profile.name
  
  # Instance automatically assumes role via IMDS (Instance Metadata Service)
}
```

**Why Instance Profile?** EC2 instances run your OS. The Instance Profile allows the instance to retrieve temporary credentials from AWS IMDS.

---

## Pattern 2: Lambda Functions (Direct Attachment)

**Flow:** Role → Policies → Attach Policies → **Attach directly to Lambda**

Lambda doesn't need Instance Profiles - it's a managed service.

### Example: Lambda with S3 Read Access

```terraform
# Step 1: Create Role with Lambda trust policy
resource "aws_iam_role" "lambda_role" {
  name = "my-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"  # Only Lambda can assume
      }
    }]
  })
}

# Step 2: Create Policy
resource "aws_iam_policy" "lambda_s3_policy" {
  name = "lambda-s3-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["s3:GetObject"]
      Resource = "arn:aws:s3:::my-bucket/*"
    }]
  })
}

# Step 3: Attach Policy to Role
resource "aws_iam_role_policy_attachment" "lambda_s3" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_s3_policy.arn
}

# Step 4: Attach Role directly to Lambda (no Instance Profile!)
resource "aws_lambda_function" "my_function" {
  filename      = "function.zip"
  function_name = "my-function"
  role          = aws_iam_role.lambda_role.arn  # Direct attachment
  handler       = "index.handler"
  runtime       = "python3.9"
}
```

**Key Difference:** Lambda uses `role` attribute directly, not `iam_instance_profile`.

---

## Pattern 3: ECS Tasks (Two Roles)

**Flow:** Create Execution Role + Task Role → Policies → Attach → **Both to Task Definition**

ECS uses two roles:
- **Execution Role**: Pulls images, writes logs (ECS service uses this)
- **Task Role**: Your application code uses this

### Example: ECS Task with S3 Access

```terraform
# Step 1: Execution Role (for ECS to pull images)
resource "aws_iam_role" "ecs_execution_role" {
  name = "ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

# Step 2: Task Role (for your application)
resource "aws_iam_role" "ecs_task_role" {
  name = "ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

# Step 3: Policies
resource "aws_iam_policy" "ecr_pull" {
  name = "ecr-pull-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage"
      ]
      Resource = "*"
    }]
  })
}

resource "aws_iam_policy" "s3_access" {
  name = "s3-access-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["s3:GetObject", "s3:PutObject"]
      Resource = "arn:aws:s3:::my-bucket/*"
    }]
  })
}

# Step 4: Attach Policies
resource "aws_iam_role_policy_attachment" "execution_ecr" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = aws_iam_policy.ecr_pull.arn
}

resource "aws_iam_role_policy_attachment" "task_s3" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.s3_access.arn
}

# Step 5: Attach both roles to Task Definition
resource "aws_ecs_task_definition" "my_task" {
  family                   = "my-task"
  requires_compatibilities = ["FARGATE"]
  network_mode            = "awsvpc"
  cpu                     = "256"
  memory                  = "512"

  # Execution role: ECS uses this to pull images
  execution_role_arn = aws_iam_role.ecs_execution_role.arn
  
  # Task role: Your application code uses this
  task_role_arn = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([{
    name  = "my-container"
    image = "my-ecr-repo:latest"
  }])
}
```

**Key Points:**
- Execution Role: Used by ECS service (pulls images, writes logs)
- Task Role: Used by your application code (S3, DynamoDB, etc.)

---

## Pattern 4: RDS (Optional Monitoring Role)

**Flow:** Role → Policies → Attach → **Attach to RDS (optional)**

RDS only uses roles for Enhanced Monitoring, not for database access.

### Example: RDS with Enhanced Monitoring

```terraform
# Step 1: Create Monitoring Role
resource "aws_iam_role" "rds_monitoring_role" {
  name = "rds-monitoring-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "monitoring.rds.amazonaws.com"
      }
    }]
  })
}

# Step 2: Attach CloudWatch policy (AWS managed)
resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  role       = aws_iam_role.rds_monitoring_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# Step 3: Attach to RDS (optional - only if using Enhanced Monitoring)
resource "aws_db_instance" "my_db" {
  identifier     = "my-database"
  engine         = "postgres"
  instance_class = "db.t3.micro"
  
  # Optional: Only needed for Enhanced Monitoring
  monitoring_interval = 60
  monitoring_role_arn = aws_iam_role.rds_monitoring_role.arn
}
```

**Note:** RDS database access uses database users/passwords, not IAM roles. Roles are only for monitoring.

---

## Pattern 5: Glue Jobs (Service Role)

**Flow:** Role → Policies → Attach → **Attach directly to Glue**

Similar to Lambda - direct attachment.

### Example: Glue Job with S3 Access

```terraform
# Step 1: Create Glue Service Role
resource "aws_iam_role" "glue_role" {
  name = "glue-service-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "glue.amazonaws.com"
      }
    }]
  })
}

# Step 2: Attach AWS managed Glue service role policy
resource "aws_iam_role_policy_attachment" "glue_service" {
  role       = aws_iam_role.glue_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

# Step 3: Attach S3 policy
resource "aws_iam_role_policy_attachment" "glue_s3" {
  role       = aws_iam_role.glue_role.name
  policy_arn = aws_iam_policy.s3_access.arn
}

# Step 4: Attach directly to Glue Job
resource "aws_glue_job" "my_job" {
  name     = "my-glue-job"
  role_arn = aws_iam_role.glue_role.arn  # Direct attachment
  command {
    script_location = "s3://my-bucket/scripts/my-script.py"
  }
}
```

---

## Pattern 6: Step Functions (Execution Role)

**Flow:** Role → Policies → Attach → **Attach directly to State Machine**

### Example: Step Function with Lambda Invoke

```terraform
# Step 1: Create Step Functions Role
resource "aws_iam_role" "sfn_role" {
  name = "step-functions-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "states.amazonaws.com"
      }
    }]
  })
}

# Step 2: Policy for Lambda invoke
resource "aws_iam_policy" "sfn_lambda" {
  name = "sfn-lambda-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["lambda:InvokeFunction"]
      Resource = aws_lambda_function.my_function.arn
    }]
  })
}

# Step 3: Attach Policy
resource "aws_iam_role_policy_attachment" "sfn_lambda" {
  role       = aws_iam_role.sfn_role.name
  policy_arn = aws_iam_policy.sfn_lambda.arn
}

# Step 4: Attach directly to State Machine
resource "aws_sfn_state_machine" "my_state_machine" {
  name     = "my-state-machine"
  role_arn = aws_iam_role.sfn_role.arn  # Direct attachment

  definition = jsonencode({
    Comment = "My State Machine"
    StartAt = "InvokeLambda"
    States = {
      InvokeLambda = {
        Type     = "Task"
        Resource = aws_lambda_function.my_function.arn
        End     = true
      }
    }
  })
}
```

---

## Comparison Table

| Service | Instance Profile? | Attachment Method | Trust Principal |
|---------|------------------|-------------------|-----------------|
| **EC2** | ✅ Required | `iam_instance_profile` | `ec2.amazonaws.com` |
| **Lambda** | ❌ No | `role` | `lambda.amazonaws.com` |
| **ECS Tasks** | ❌ No | `execution_role_arn` + `task_role_arn` | `ecs-tasks.amazonaws.com` |
| **RDS** | ❌ No | `monitoring_role_arn` (optional) | `monitoring.rds.amazonaws.com` |
| **Glue** | ❌ No | `role_arn` | `glue.amazonaws.com` |
| **Step Functions** | ❌ No | `role_arn` | `states.amazonaws.com` |
| **EKS Pods** | ❌ No | Via Service Account annotation | `eks.amazonaws.com` |

---

## Key Takeaways

1. **EC2 is unique** - Only service requiring Instance Profiles
2. **Trust Policy matters** - Each service has a specific Principal (ec2, lambda, ecs-tasks, etc.)
3. **Pattern is consistent** - Role → Policies → Attach → Attach to Resource
4. **Attachment method varies** - Some use `role`, some use `role_arn`, EC2 uses `iam_instance_profile`

---

## Real-World Example: Our Diagram Maker Project

In our `terraform/modules/app_instance/main.tf`, we use **Pattern 1 (EC2)**:

```terraform
# 1. Create Role
resource "aws_iam_role" "ec2_role" { ... }

# 2. Create Policies
resource "aws_iam_policy" "bedrock_policy" { ... }
resource "aws_iam_policy" "s3_policy" { ... }
resource "aws_iam_policy" "ecr_policy" { ... }

# 3. Attach Policies
resource "aws_iam_role_policy_attachment" "bedrock_attachment" { ... }
resource "aws_iam_role_policy_attachment" "s3_attachment" { ... }
resource "aws_iam_role_policy_attachment" "ecr_attachment" { ... }

# 4. Create Instance Profile (EC2-specific!)
resource "aws_iam_instance_profile" "ec2_profile" {
  role = aws_iam_role.ec2_role.name
}

# 5. Attach Profile to EC2
resource "aws_instance" "diagram_maker_app" {
  iam_instance_profile = aws_iam_instance_profile.ec2_profile.name
}
```

This is the correct pattern for EC2 instances!



