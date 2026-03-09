variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "AWS CLI profile to use"
  type        = string
  default     = "terraform-pipeline"
}

variable "project_name" {
  description = "Project name — used as prefix for all resource names"
  type        = string
  default     = "yt-summarizer"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}