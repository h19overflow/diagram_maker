# Output: EC2 Instance ID
# Unique identifier for the created EC2 instance
# Useful for connecting via AWS CLI or referencing in other Terraform configurations
output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.diagram_maker_app.id
}

# Output: EC2 Instance Public IP
# Public IP address that can be used to access the instance from the internet
# Note: This may change if the instance is stopped/started (use Elastic IP for static address)
output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.diagram_maker_app.public_ip
}

# Output: EC2 Instance Private IP
# Private IP address within the VPC
# Used for internal communication between AWS resources (e.g., RDS, other EC2 instances)
output "instance_private_ip" {
  description = "Private IP address of the EC2 instance"
  value       = aws_instance.diagram_maker_app.private_ip
}

# Output: IAM Role ARN
# Amazon Resource Name of the IAM role attached to the instance
# Useful for debugging permissions or referencing in other IAM policies
output "iam_role_arn" {
  description = "ARN of the IAM role attached to the EC2 instance"
  value       = aws_iam_role.ec2_role.arn
}

# Output: IAM Instance Profile Name
# Name of the instance profile that wraps the IAM role
# Can be used to attach the same profile to other instances if needed
output "iam_instance_profile_name" {
  description = "Name of the IAM instance profile"
  value       = aws_iam_instance_profile.ec2_profile.name
}
