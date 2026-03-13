# ═══════════════════════════════════════════════════════════
# YT Summarizer — Root outputs
# terraform/outputs.tf
# ═══════════════════════════════════════════════════════════

# ── API ──────────────────────────────────────────────────────
output "api_url" {
  description = "Endpoint completo de la API para resumir videos."
  value       = module.api_gateway.api_url
}

# ── Lambda ───────────────────────────────────────────────────
output "lambda_function_name" {
  description = "Nombre de la función Lambda."
  value       = module.lambda.function_name
}

# ── DynamoDB ─────────────────────────────────────────────────
output "dynamodb_table_name" {
  description = "Nombre de la tabla DynamoDB."
  value       = module.dynamodb.table_name
}

# ── Frontend ─────────────────────────────────────────────────
output "frontend_bucket" {
  description = "Nombre del bucket S3 donde se hostea el frontend."
  value       = module.storage.bucket_name
}

output "frontend_url" {
  description = "URL pública del frontend via CloudFront."
  value       = module.storage.cloudfront_url
}

output "cloudfront_distribution_id" {
  description = "ID de la distribución CloudFront. Usarlo para invalidar caché después de un deploy."
  value       = module.storage.cloudfront_distribution_id
}
