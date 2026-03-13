# ═══════════════════════════════════════════════════════════
# YT Summarizer — Root configuration
# terraform/main.tf
# ═══════════════════════════════════════════════════════════

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
      Repository  = "github.com/EmmaLedesma/youtube-summarizer"
    }
  }
}

# ── DynamoDB ─────────────────────────────────────────────────
module "dynamodb" {
  source = "./modules/dynamodb"

  table_name = "${var.project_name}-${var.environment}-summaries"
}

# ── Lambda ───────────────────────────────────────────────────
module "lambda" {
  source = "./modules/lambda"

  function_name      = "${var.project_name}-${var.environment}-summarizer"
  zip_path           = "../backend/summarizer/summarizer.zip"
  dynamodb_table_arn = module.dynamodb.table_arn

  environment_variables = {
    DYNAMODB_TABLE   = "${var.project_name}-${var.environment}-summaries"
    AWS_REGION_NAME  = var.aws_region
  }
}

# ── API Gateway ──────────────────────────────────────────────
module "api_gateway" {
  source = "./modules/api-gateway"

  api_name             = "${var.project_name}-${var.environment}-api"
  lambda_invoke_arn    = module.lambda.invoke_arn
  lambda_function_name = module.lambda.function_name
}

# ── Storage (S3 + CloudFront) ────────────────────────────────
module "storage" {
  source = "./modules/storage"

  project_name = var.project_name
  environment  = var.environment
}
