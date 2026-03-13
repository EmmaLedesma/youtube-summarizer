# terraform/modules/monitoring/variables.tf

variable "project_name" {
  description = "Nombre del proyecto"
  type        = string
}

variable "environment" {
  description = "Ambiente (dev, prod)"
  type        = string
}

variable "aws_region" {
  description = "Region AWS"
  type        = string
  default     = "us-east-1"
}

variable "lambda_function_name" {
  description = "Nombre de la función Lambda"
  type        = string
}

variable "api_name" {
  description = "Nombre del API Gateway"
  type        = string
}

variable "dynamodb_table_name" {
  description = "Nombre de la tabla DynamoDB"
  type        = string
}
