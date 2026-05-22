# infrastructure/outputs.tf

output "ec2_public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_eip.main.public_ip
}

output "ec2_public_dns" {
  description = "Public DNS of the EC2 instance"
  value       = aws_instance.main.public_dns
}

output "api_url" {
  description = "FastAPI backend URL"
  value       = "http://${aws_eip.main.public_ip}:8000"
}

output "frontend_url" {
  description = "React frontend URL"
  value       = "http://${aws_s3_bucket_website_configuration.frontend.website_endpoint}"
}

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = aws_db_instance.postgres.address
  sensitive   = true
}

output "redis_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = aws_elasticache_cluster.redis.cache_nodes[0].address
  sensitive   = true
}

output "uploads_bucket" {
  description = "S3 uploads bucket name"
  value       = aws_s3_bucket.uploads.id
}

output "frontend_bucket" {
  description = "S3 frontend bucket name"
  value       = aws_s3_bucket.frontend.id
}

output "elastic_ip" {
  value = aws_eip.main.public_ip
}