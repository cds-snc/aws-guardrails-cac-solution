# Variables for AWS S3 CSV to Slack Lambda Function

# AWS Configuration
variable "aws_region" {
  description = "AWS region where resources will be deployed"
  type        = string
  default     = "ca-central-1"
}

variable "aws_account_id" {
  description = "AWS Account ID for security validation"
  type        = string
  default     = "886481071419"
}

# S3 and Lambda Configuration
variable "s3_bucket_name" {
  description = "Name of the S3 bucket containing the CSV files"
  type        = string
}

variable "lambda_source_dir" {
  description = "Path to the Lambda function source directory"
  type        = string
  default     = "../src/lambda/aws_s3_csv_to_slack"
}

variable "slack_webhook_url" {
  description = "Slack webhook URL for sending notifications"
  type        = string
  sensitive   = true
}

variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "billing_code" {
  description = "Billing code for cost tracking and resource tagging"
  type        = string
  default     = "guardrails"
}

# Monitoring Configuration
variable "log_retention_days" {
  description = "Number of days to retain CloudWatch logs"
  type        = number
  default     = 14
}

# Scheduling Configuration
variable "schedule_expression" {
  description = "Cron expression for Lambda execution schedule"
  type        = string
  default     = "cron(0 13 * * ? *)" # 5am PST (13:00 UTC)
}