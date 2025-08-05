# AWS Guardrails CAC Solution - Main Configuration
# This file contains the primary provider configuration and data sources

# Primary AWS provider for ca-central-1
provider "aws" {
  region              = var.aws_region
  allowed_account_ids = [var.aws_account_id]

  default_tags {
    tags = local.common_tags
  }
}

# Secondary AWS provider for us-east-1 (for resources that require us-east-1)
provider "aws" {
  alias               = "us-east-1"
  region              = "us-east-1"
  allowed_account_ids = [var.aws_account_id]

  default_tags {
    tags = local.common_tags
  }
}

# Data sources for account and region information
data "aws_caller_identity" "current" {}

data "aws_region" "current" {}