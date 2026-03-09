resource "aws_dynamodb_table" "summaries" {
  name         = var.table_name
  billing_mode = var.billing_mode
  hash_key     = "videoId"
  range_key    = "createdAt"

  attribute {
    name = "videoId"
    type = "S"
  }

  attribute {
    name = "createdAt"
    type = "S"
  }

  # TTL: items se auto-eliminan después de ttl_days
  ttl {
    attribute_name = "expiresAt"
    enabled        = var.ttl_days > 0
  }

  # Point-in-time recovery — buena práctica, sin costo adicional significativo
  point_in_time_recovery {
    enabled = true
  }

  tags = merge(var.tags, {
    Module = "dynamodb"
  })
}