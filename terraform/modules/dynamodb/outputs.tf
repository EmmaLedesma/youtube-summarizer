output "table_name" {
  description = "DynamoDB table name"
  value       = aws_dynamodb_table.summaries.name
}

output "table_arn" {
  description = "DynamoDB table ARN — used by IAM policies"
  value       = aws_dynamodb_table.summaries.arn
}