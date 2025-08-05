# AWS Guardrails CAC Solution - Terraform Deployment

This comprehensive Terraform configuration deploys an enterprise-grade AWS compliance monitoring solution that processes CSV files from S3 and sends professionally formatted alerts to Slack. The solution includes automated scheduling, monitoring, and encrypted notifications.

## 🏗️ Architecture

### **Core Components:**
- **Lambda Function**: `guardrails-cac-s3-csv-to-slack` - Processes CSV files with smart filtering
- **EventBridge Rule**: Daily execution at 5am PST with configurable scheduling
- **SNS Topic**: Encrypted notifications for CloudWatch alarms
- **IAM Roles & Policies**: Least-privilege security with comprehensive permissions
- **CloudWatch Resources**: Alarms, logs, and monitoring with configurable retention

### **Enhanced Features:**
- **Smart Filtering**: Excludes `AWS::::Account` resource types to reduce noise
- **Professional Slack Formatting**: Rich message blocks with organized information
- **Comprehensive Monitoring**: Error and duration alarms with SNS integration
- **Enterprise Security**: KMS encryption, account validation, and least-privilege IAM

## 📁 Terraform File Structure

```
terraform/
├── main.tf                    # Provider configuration & data sources
├── versions.tf                # Terraform & provider version requirements  
├── locals.tf                  # Computed values & common configuration
├── variables.tf               # Input variable definitions
├── lambda.tf                  # Lambda function & IAM resources
├── eventbridge.tf             # EventBridge scheduling resources
├── alarms.tf                  # CloudWatch monitoring & alerting
├── sns.tf                     # SNS topic for notifications
├── outputs.tf                 # Output values
├── terraform.tfvars.example   # Example configuration file
├── terragrunt.hcl            # Terragrunt configuration
└── README.md                  # This documentation
```

## 🚀 Quick Start

### **Option 1: Terragrunt (Recommended)**
```bash
# Navigate to terraform directory
cd terraform/

# Copy and configure variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your specific values

# Deploy with Terragrunt
terragrunt plan
terragrunt apply
```

### **Option 2: Standalone Terraform**
```bash
# Navigate to terraform directory
cd terraform/

# Initialize Terraform
terraform init

# Copy and configure variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your specific values

# Deploy
terraform validate
terraform plan
terraform apply
```

## ⚙️ Prerequisites

1. **Terraform**: Version >= 1.5
2. **AWS CLI**: Configured with appropriate credentials
3. **Terragrunt**: (Optional) For enhanced deployment experience
4. **S3 Bucket**: Must exist and contain CSV compliance files
5. **Slack Webhook**: (Optional) For Slack notifications

## 🔧 Configuration

### **Required Variables in terraform.tfvars:**
```hcl
# AWS Configuration
aws_region     = "ca-central-1"
aws_account_id = "886481071419"

# S3 bucket containing the CSV compliance files
s3_bucket_name = "gc-fedclient-886481071419-ca-central-1"

# Slack webhook URL for notifications
slack_webhook_url = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
```

### **Optional Configuration:**
```hcl
# Environment and tagging
environment   = "prod"
billing_code  = "guardrails"

# Monitoring configuration  
log_retention_days = 14

# Scheduling configuration (5am PST = 13:00 UTC)
schedule_expression = "cron(0 13 * * ? *)"

# Lambda source directory (handled automatically by Terragrunt)
# lambda_source_dir = "../src/lambda/aws_s3_csv_to_slack"
```

## 📦 What Gets Deployed

### **Lambda Resources:**
- **Function**: `guardrails-cac-s3-csv-to-slack` (Python 3.9, 512MB, 5min timeout)
- **IAM Role**: Least-privilege S3 and CloudWatch access
- **Log Group**: `/aws/lambda/guardrails-cac-s3-csv-to-slack` (14-day retention)

### **Scheduling & Events:**
- **EventBridge Rule**: `guardrails-cac-daily-compliance-check`
- **Lambda Permission**: Allows EventBridge to invoke function
- **Automated Trigger**: Daily at 5:00 AM PST (13:00 UTC)

### **Monitoring & Alerts:**
- **SNS Topic**: `guardrails-cac-alerts` (KMS encrypted)
- **Error Alarm**: Triggers on any Lambda function errors
- **Duration Alarm**: Triggers if execution exceeds 4 minutes
- **Email Notifications**: Optional SNS email subscriptions

### **Security Features:**
- **KMS Encryption**: SNS topic encrypted with AWS managed key
- **Account Validation**: Resources restricted to your AWS account
- **Least Privilege**: IAM policies with minimal required permissions
- **Resource Tagging**: Comprehensive cost tracking and management

## 🕐 Scheduling Details

The Lambda function is scheduled to run daily at **5:00 AM PST** using the cron expression `cron(0 13 * * ? *)` (13:00 UTC).

**Daylight Saving Time Note**: This schedule uses fixed UTC time and does not automatically adjust for DST. During PDT (Pacific Daylight Time), the function runs at 6:00 AM local time. For year-round 5:00 AM local time, manually update the `schedule_expression` variable:

- **PST (UTC-8)**: `cron(0 13 * * ? *)` - 5:00 AM PST
- **PDT (UTC-7)**: `cron(0 12 * * ? *)` - 5:00 AM PDT

## 📊 Lambda Function Behavior

### **Enhanced Processing:**
1. **S3 Integration**: Scans bucket and selects latest CSV file by modification date
2. **Intelligent Parsing**: Extracts `NON_COMPLIANT` items with validation
3. **Smart Filtering**: Excludes `AWS::::Account` resource types to reduce noise
4. **Professional Formatting**: Creates rich Slack messages with organized sections
5. **Comprehensive Logging**: Detailed logs for audit and troubleshooting

### **Slack Notification Features:**
- **Rich Message Blocks**: Professional formatting with headers and sections
- **Guardrail Grouping**: Organizes items by guardrail for better readability  
- **Smart Truncation**: Handles long ARNs with intelligent shortening
- **Item Limits**: Shows up to 8 detailed items (prevents message size issues)
- **Status Updates**: Notifications for both alarm and recovery states

### **Error Handling:**
- **Retry Logic**: Automatic retries for AWS API calls with exponential backoff
- **Graceful Degradation**: Continues processing on non-critical errors
- **Comprehensive Monitoring**: CloudWatch alarms for errors and performance

## 📧 Environment Variables

The Lambda function uses these environment variables (automatically configured by Terraform):

- **`S3_BUCKET`**: Name of the S3 bucket containing CSV files (required)
- **`SLACK_WEBHOOK_URL`**: Slack webhook URL for notifications (optional)

## 📈 Monitoring & Alerting

### **CloudWatch Alarms:**
- **`guardrails-cac-s3-csv-to-slack-errors`**: Triggers on function errors (threshold: > 0)
- **`guardrails-cac-s3-csv-to-slack-duration`**: Triggers on long execution (threshold: > 4 minutes)

### **SNS Integration:**
- **Encrypted Topic**: `guardrails-cac-alerts` with AWS managed KMS key
- **Alarm Actions**: Notifications sent for both ALARM and OK states
- **Email Subscriptions**: Optional email notifications for alarm states

### **CloudWatch Logs:**
- **Log Group**: `/aws/lambda/guardrails-cac-s3-csv-to-slack`
- **Retention**: 14 days (configurable via `log_retention_days`)
- **Structured Logging**: JSON format for easy parsing and analysis

## 📤 Terraform Outputs

After successful deployment, Terraform provides these useful outputs:

### **Lambda Outputs:**
- **`lambda_function_name`**: `guardrails-cac-s3-csv-to-slack`
- **`lambda_function_arn`**: Full ARN of the Lambda function
- **`lambda_role_arn`**: ARN of the Lambda execution role
- **`cloudwatch_log_group_name`**: CloudWatch log group path

### **EventBridge Outputs:**
- **`eventbridge_rule_name`**: Name of the scheduling rule
- **`eventbridge_rule_arn`**: ARN of the EventBridge rule
- **`schedule_expression`**: Current cron expression

### **Monitoring Outputs:**
- **`sns_topic_arn`**: ARN of the encrypted SNS topic
- **`error_alarm_name`**: Name of the error monitoring alarm
- **`duration_alarm_name`**: Name of the duration monitoring alarm

## 🧪 Testing & Validation

### **Manual Function Testing:**
```bash
# Invoke the Lambda function manually
aws lambda invoke \
  --function-name guardrails-cac-s3-csv-to-slack \
  --payload '{"source":"manual-test"}' \
  response.json && cat response.json
```

### **Expected Response:**
```json
{
  "status": "success",
  "csv_file": "compliance_report_2025-08-05.csv", 
  "non_compliant_count": 3,
  "non_compliant_items": [
    {
      "accountId": "123456789012",
      "guardrail": "07-Protection of Data-in-Transit",
      "controlName": "gc07_check_certificate_authorities",
      "resourceType": "AWS::ACM::Certificate",
      "resourceArn": "arn:aws:acm:ca-central-1:123456789012:certificate/abc123"
    }
  ]
}
```

### **Monitoring Validation:**
```bash
# Check CloudWatch logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/guardrails-cac"

# Check alarm status  
aws cloudwatch describe-alarms --alarm-names \
  "guardrails-cac-s3-csv-to-slack-errors" \
  "guardrails-cac-s3-csv-to-slack-duration"

# Test SNS topic
aws sns list-subscriptions-by-topic --topic-arn $(terraform output -raw sns_topic_arn)
```

## 🔧 Troubleshooting

### **Common Issues:**

| Issue | Solution |
|-------|----------|
| **Archive creation error** | Ensure Lambda source code exists at `../src/lambda/aws_s3_csv_to_slack` |
| **Access denied on S3** | Verify IAM policy and S3 bucket permissions |
| **No CSV files found** | Check S3 bucket contains `.csv` files and Lambda has `s3:ListBucket` |
| **Slack notifications fail** | Validate webhook URL and test manually with curl |
| **Function timeouts** | Check CloudWatch logs and consider increasing timeout |

### **Debugging Commands:**
```bash
# View recent Lambda logs
aws logs describe-log-streams \
  --log-group-name "/aws/lambda/guardrails-cac-s3-csv-to-slack" \
  --order-by LastEventTime --descending --max-items 5

# Get specific log events  
aws logs get-log-events \
  --log-group-name "/aws/lambda/guardrails-cac-s3-csv-to-slack" \
  --log-stream-name "2025/08/05/[\$LATEST]abc123..."

# Check EventBridge rule status
aws events describe-rule --name "guardrails-cac-daily-compliance-check"
```

## 🔒 Security Best Practices

- **✅ KMS Encryption**: SNS topic encrypted with AWS managed keys
- **✅ Least Privilege IAM**: Minimal required permissions for S3 and logging
- **✅ Account Validation**: Resources restricted to your AWS account only
- **✅ Sensitive Variables**: Slack webhook URL marked as sensitive in Terraform
- **✅ Resource Tagging**: Comprehensive tagging for cost tracking and compliance
- **✅ Network Security**: Function runs in AWS managed environment (no VPC required)

## 💰 Cost Considerations

### **Estimated Monthly Costs:**
- **Lambda**: ~$1-3 USD (daily execution, avg 2-minute runtime)
- **CloudWatch Logs**: ~$1 USD (14-day retention, moderate log volume)  
- **SNS Topic**: Free tier covers alarm notifications
- **EventBridge**: ~$0.10 USD (daily rule execution)
- **CloudWatch Alarms**: ~$0.20 USD (2 alarms)

**Total Estimated Cost**: < $5 USD/month for comprehensive compliance monitoring

## 🧹 Cleanup

To destroy all resources:

```bash
terraform destroy
```

## Troubleshooting

1. **Check CloudWatch Logs**: `/aws/lambda/s3-csv-to-slack`
2. **Verify S3 Permissions**: Ensure the Lambda role can read the S3 bucket
3. **Test Slack Webhook**: Verify the webhook URL is correct and accessible
4. **Check EventBridge Rule**: Ensure the rule is enabled and properly configured

## Cost Considerations

- **Lambda**: Charges based on requests and execution time
- **CloudWatch Logs**: 14-day retention for cost optimization
- **EventBridge**: Minimal cost for daily rule execution
- **CloudWatch Alarms**: Standard alarm pricing

Estimated monthly cost for daily execution: < $5 USD
