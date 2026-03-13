# ═══════════════════════════════════════════════════════════
# Module: storage — outputs.tf
# ═══════════════════════════════════════════════════════════

output "bucket_name" {
  description = "Nombre del bucket S3 donde se sube el frontend."
  value       = aws_s3_bucket.frontend.id
}

output "bucket_arn" {
  description = "ARN del bucket S3."
  value       = aws_s3_bucket.frontend.arn
}

output "cloudfront_domain" {
  description = "Dominio de CloudFront (sin https://)."
  value       = aws_cloudfront_distribution.frontend.domain_name
}

output "cloudfront_url" {
  description = "URL completa del frontend con https."
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}

output "cloudfront_distribution_id" {
  description = "ID de la distribución CloudFront. Necesario para invalidaciones de caché."
  value       = aws_cloudfront_distribution.frontend.id
}
