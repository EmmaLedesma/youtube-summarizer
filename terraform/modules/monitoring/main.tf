# ═══════════════════════════════════════════════════════════
# YT Summarizer — CloudWatch Dashboard + Alarms
# terraform/modules/monitoring/main.tf
# ═══════════════════════════════════════════════════════════

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.project_name}-${var.environment}"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "text"
        x      = 0
        y      = 0
        width  = 24
        height = 2
        properties = {
          markdown = "# YT Summarizer — ${upper(var.environment)}\nMonitoreo en tiempo real · Lambda · API Gateway · DynamoDB"
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 2
        width  = 8
        height = 6
        properties = {
          title   = "Lambda — Invocaciones"
          view    = "timeSeries"
          stat    = "Sum"
          period  = 300
          region  = var.aws_region
          metrics = [["AWS/Lambda", "Invocations", "FunctionName", var.lambda_function_name]]
        }
      },
      {
        type   = "metric"
        x      = 8
        y      = 2
        width  = 8
        height = 6
        properties = {
          title  = "Lambda — Errores"
          view   = "timeSeries"
          stat   = "Sum"
          period = 300
          region = var.aws_region
          metrics = [
            ["AWS/Lambda", "Errors",    "FunctionName", var.lambda_function_name, { color = "#d62728" }],
            ["AWS/Lambda", "Throttles", "FunctionName", var.lambda_function_name, { color = "#ff7f0e" }]
          ]
        }
      },
      {
        type   = "metric"
        x      = 16
        y      = 2
        width  = 8
        height = 6
        properties = {
          title  = "Lambda — Duración (ms)"
          view   = "timeSeries"
          period = 300
          region = var.aws_region
          metrics = [
            ["AWS/Lambda", "Duration", "FunctionName", var.lambda_function_name, { stat = "p50",     label = "p50" }],
            ["AWS/Lambda", "Duration", "FunctionName", var.lambda_function_name, { stat = "p95",     label = "p95" }],
            ["AWS/Lambda", "Duration", "FunctionName", var.lambda_function_name, { stat = "Maximum", label = "Max" }]
          ]
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 8
        width  = 8
        height = 6
        properties = {
          title   = "API Gateway — Requests"
          view    = "timeSeries"
          stat    = "Sum"
          period  = 300
          region  = var.aws_region
          metrics = [["AWS/ApiGateway", "Count", "ApiName", var.api_name]]
        }
      },
      {
        type   = "metric"
        x      = 8
        y      = 8
        width  = 8
        height = 6
        properties = {
          title  = "API Gateway — Latencia (ms)"
          view   = "timeSeries"
          period = 300
          region = var.aws_region
          metrics = [
            ["AWS/ApiGateway", "Latency",            "ApiName", var.api_name, { stat = "p50", label = "p50" }],
            ["AWS/ApiGateway", "Latency",            "ApiName", var.api_name, { stat = "p95", label = "p95" }],
            ["AWS/ApiGateway", "IntegrationLatency", "ApiName", var.api_name, { stat = "p50", label = "Integration p50" }]
          ]
        }
      },
      {
        type   = "metric"
        x      = 16
        y      = 8
        width  = 8
        height = 6
        properties = {
          title  = "API Gateway — Errores 4xx / 5xx"
          view   = "timeSeries"
          stat   = "Sum"
          period = 300
          region = var.aws_region
          metrics = [
            ["AWS/ApiGateway", "4XXError", "ApiName", var.api_name, { color = "#ff7f0e", label = "4xx" }],
            ["AWS/ApiGateway", "5XXError", "ApiName", var.api_name, { color = "#d62728", label = "5xx" }]
          ]
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 14
        width  = 8
        height = 6
        properties = {
          title  = "DynamoDB — Operaciones (caché)"
          view   = "timeSeries"
          period = 300
          region = var.aws_region
          metrics = [
            ["AWS/DynamoDB", "SuccessfulRequestLatency", "TableName", var.dynamodb_table_name, "Operation", "GetItem", { stat = "SampleCount", label = "GetItem (caché hit)" }],
            ["AWS/DynamoDB", "SuccessfulRequestLatency", "TableName", var.dynamodb_table_name, "Operation", "PutItem", { stat = "SampleCount", label = "PutItem (nuevo)" }]
          ]
        }
      },
      {
        type   = "metric"
        x      = 8
        y      = 14
        width  = 8
        height = 6
        properties = {
          title  = "DynamoDB — Latencia (ms)"
          view   = "timeSeries"
          period = 300
          region = var.aws_region
          metrics = [
            ["AWS/DynamoDB", "SuccessfulRequestLatency", "TableName", var.dynamodb_table_name, "Operation", "GetItem", { stat = "p50", label = "GetItem p50" }],
            ["AWS/DynamoDB", "SuccessfulRequestLatency", "TableName", var.dynamodb_table_name, "Operation", "PutItem", { stat = "p50", label = "PutItem p50" }]
          ]
        }
      },
      {
        type   = "metric"
        x      = 16
        y      = 14
        width  = 8
        height = 6
        properties = {
          title   = "Lambda — Ejecuciones Concurrentes"
          view    = "timeSeries"
          stat    = "Maximum"
          period  = 300
          region  = var.aws_region
          metrics = [["AWS/Lambda", "ConcurrentExecutions", "FunctionName", var.lambda_function_name]]
        }
      }
    ]
  })
}

# ── Alarma: Lambda Errores ───────────────────────────────────
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "${var.project_name}-${var.environment}-lambda-errors"
  alarm_description   = "Lambda tiene errores en los ultimos 5 minutos"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 3
  treat_missing_data  = "notBreaching"
  dimensions = {
    FunctionName = var.lambda_function_name
  }
}

# ── Alarma: Lambda Duración alta ────────────────────────────
resource "aws_cloudwatch_metric_alarm" "lambda_duration" {
  alarm_name          = "${var.project_name}-${var.environment}-lambda-duration"
  alarm_description   = "Lambda p95 supera los 25 segundos"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = 300
  extended_statistic  = "p95"
  threshold           = 25000
  treat_missing_data  = "notBreaching"
  dimensions = {
    FunctionName = var.lambda_function_name
  }
}

# ── Alarma: API Gateway 5xx ──────────────────────────────────
resource "aws_cloudwatch_metric_alarm" "api_5xx" {
  alarm_name          = "${var.project_name}-${var.environment}-api-5xx"
  alarm_description   = "API Gateway tiene errores 5xx"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "5XXError"
  namespace           = "AWS/ApiGateway"
  period              = 300
  statistic           = "Sum"
  threshold           = 3
  treat_missing_data  = "notBreaching"
  dimensions = {
    ApiName = var.api_name
  }
}
