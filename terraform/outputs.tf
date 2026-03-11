output "dynamodb_table_name" {
  description = "DynamoDB summaries table name"
  value       = module.dynamodb.table_name
}

output "dynamodb_table_arn" {
  description = "DynamoDB summaries table ARN"
  value       = module.dynamodb.table_arn
}

output "lambda_summarizer_name" {
  description = "Summarizer Lambda function name"
  value       = module.lambda_summarizer.function_name
}

output "lambda_summarizer_invoke_arn" {
  description = "Summarizer Lambda invoke ARN"
  value       = module.lambda_summarizer.invoke_arn
}