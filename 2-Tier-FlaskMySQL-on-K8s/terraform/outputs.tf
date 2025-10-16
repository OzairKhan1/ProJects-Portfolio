# ===========================
# EC2 Instance Outputs
# ===========================

# Networking
output "ec2_public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.terraInstance.public_ip
}

output "ec2_public_dns" {
  description = "Public DNS of the EC2 instance"
  value       = aws_instance.terraInstance.public_dns
}

output "ec2_private_ip" {
  description = "Private IP of the EC2 instance"
  value       = aws_instance.terraInstance.private_ip
}

output "ec2_private_dns" {
  description = "Private DNS of the EC2 instance"
  value       = aws_instance.terraInstance.private_dns
}

# Identity
output "ec2_instance_id" {
  description = "Instance ID of the EC2 instance"
  value       = aws_instance.terraInstance.id
}

output "ec2_availability_zone" {
  description = "Availability Zone where the EC2 is running"
  value       = aws_instance.terraInstance.availability_zone
}

output "ec2_arn" {
  description = "ARN of the EC2 instance"
  value       = aws_instance.terraInstance.arn
}

# Storage & Security
output "ec2_key_name" {
  description = "Key pair name used for the EC2 instance"
  value       = aws_instance.terraInstance.key_name
}

output "ec2_root_volume_id" {
  description = "Root EBS volume ID of the EC2 instance"
  value       = aws_instance.terraInstance.root_block_device[0].volume_id
}

output "ec2_security_groups" {
  description = "VPC Security Groups attached to the EC2 instance"
  value       = aws_instance.terraInstance.vpc_security_group_ids
}

# Meta
output "ec2_tags" {
  description = "Tags assigned to the EC2 instance"
  value       = aws_instance.terraInstance.tags
}

output "ec2_ami" {
  description = "AMI ID used to launch the EC2 instance"
  value       = aws_instance.terraInstance.ami
}

