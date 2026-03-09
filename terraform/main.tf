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