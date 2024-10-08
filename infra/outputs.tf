output "instance_public_ip" {
  description = "The public IP address of the EC2 instance"
  value       = aws_instance.restaurant_api.public_ip
}

output "secrets_manager_arn" {
  description = "The ARN of the Secrets Manager secret"
  value       = aws_secretsmanager_secret.restaurant_api_secrets.arn
}

output "instance_id" {
  description = "The ID of the EC2 instance"
  value       = aws_instance.restaurant_api.id
}