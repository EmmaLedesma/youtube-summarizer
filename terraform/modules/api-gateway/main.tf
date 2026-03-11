# ── REST API ─────────────────────────────────────────────────────
resource "aws_api_gateway_rest_api" "this" {
  name        = var.api_name
  description = "YouTube Summarizer API"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = var.tags
}

# ── Resource: /summarize ─────────────────────────────────────────
resource "aws_api_gateway_resource" "summarize" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_rest_api.this.root_resource_id
  path_part   = "summarize"
}

# ── Method: POST /summarize ──────────────────────────────────────
resource "aws_api_gateway_method" "post_summarize" {
  rest_api_id   = aws_api_gateway_rest_api.this.id
  resource_id   = aws_api_gateway_resource.summarize.id
  http_method   = "POST"
  authorization = "NONE"
}

# ── Integration: POST → Lambda ───────────────────────────────────
resource "aws_api_gateway_integration" "post_summarize" {
  rest_api_id             = aws_api_gateway_rest_api.this.id
  resource_id             = aws_api_gateway_resource.summarize.id
  http_method             = aws_api_gateway_method.post_summarize.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn
}

# ── Method: OPTIONS /summarize (CORS preflight) ──────────────────
resource "aws_api_gateway_method" "options_summarize" {
  rest_api_id   = aws_api_gateway_rest_api.this.id
  resource_id   = aws_api_gateway_resource.summarize.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "options_summarize" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  resource_id = aws_api_gateway_resource.summarize.id
  http_method = aws_api_gateway_method.options_summarize.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "options_200" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  resource_id = aws_api_gateway_resource.summarize.id
  http_method = aws_api_gateway_method.options_summarize.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "options_200" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  resource_id = aws_api_gateway_resource.summarize.id
  http_method = aws_api_gateway_method.options_summarize.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type'"
    "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }

  depends_on = [aws_api_gateway_integration.options_summarize]
}

# ── Deployment ───────────────────────────────────────────────────
resource "aws_api_gateway_deployment" "this" {
  rest_api_id = aws_api_gateway_rest_api.this.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.summarize.id,
      aws_api_gateway_method.post_summarize.id,
      aws_api_gateway_integration.post_summarize.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    aws_api_gateway_integration.post_summarize,
    aws_api_gateway_integration.options_summarize,
  ]
}

# ── Stage: dev ───────────────────────────────────────────────────
resource "aws_api_gateway_stage" "dev" {
  rest_api_id   = aws_api_gateway_rest_api.this.id
  deployment_id = aws_api_gateway_deployment.this.id
  stage_name    = "dev"

  tags = var.tags
}

# ── Permission: API Gateway puede invocar la Lambda ──────────────
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.this.execution_arn}/*/*"
}