output "dynamodb_table_name" {
  description = "DynamoDB summaries table name"
  value       = module.dynamodb.table_name
}

output "dynamodb_table_arn" {
  description = "DynamoDB summaries table ARN"
  value       = module.dynamodb.table_arn
}