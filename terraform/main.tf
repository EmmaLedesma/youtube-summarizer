terraform {
  required_version = ">= 1.7"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Backend S3 — lo configuramos en el siguiente paso
  # backend "s3" {}
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

# ── Módulo DynamoDB ──────────────────────────────────────────────
module "dynamodb" {
  source = "./modules/dynamodb"

  table_name = "${var.project_name}-${var.environment}-summaries"
  ttl_days   = 90

  tags = {
    Component = "database"
  }
}

# ── Módulo Lambda Summarizer ─────────────────────────────────────
module "lambda_summarizer" {
  source = "./modules/lambda"

  function_name = "${var.project_name}-${var.environment}-summarizer"
  zip_path      = "${path.module}/../backend/summarizer/summarizer.zip"
  timeout       = 60
  memory_size   = 256

  dynamodb_table_arn = module.dynamodb.table_arn

  environment_variables = {
    DYNAMODB_TABLE  = module.dynamodb.table_name
    AWS_REGION_NAME = var.aws_region
  }

  tags = {
    Component = "compute"
  }
}

# ── Módulo API Gateway ───────────────────────────────────────────
module "api_gateway" {
  source = "./modules/api-gateway"

  api_name             = "${var.project_name}-${var.environment}-api"
  lambda_invoke_arn    = module.lambda_summarizer.invoke_arn
  lambda_function_name = module.lambda_summarizer.function_name

  tags = {
    Component = "api"
  }
}