variable "aws_region" {
  description = "AWS region to deploy to"
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Project name used for naming resources"
  type        = string
  default     = "flowspace"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "db_password" {
  description = "PostgreSQL database password"
  type        = string
  sensitive   = true
}

variable "secret_key" {
  description = "FastAPI secret key for JWT"
  type        = string
  sensitive   = true
}

variable "mongodb_url" {
  description = "MongoDB Atlas connection URL"
  type        = string
  sensitive   = true
}