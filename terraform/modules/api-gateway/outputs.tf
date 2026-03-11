output "api_url" {
  description = "Base URL of the API Gateway endpoint"
  value       = "${aws_api_gateway_stage.dev.invoke_url}/summarize"
}

output "api_id" {
  description = "API Gateway REST API ID"
  value       = aws_api_gateway_rest_api.this.id
}