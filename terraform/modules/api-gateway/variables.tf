variable "api_name" {
  description = "Name of the REST API"
  type        = string
}

variable "lambda_invoke_arn" {
  description = "Lambda invoke ARN for integration"
  type        = string
}

variable "lambda_function_name" {
  description = "Lambda function name for permission"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}