variable "aws_region" {
  description = "The AWS region to deploy the resources in"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "The environment to deploy the resources in"
  type        = string
  default     = "prod"
}

variable "grafana_url" {
  description = "The URL of the Grafana instance"
  type        = string
}

variable "grafana_access_token" {
  description = "The access token for the Grafana instance, can be found in the Grafana UI under the user menu > API keys, can be stored in the terraform.auto.tfvars file, or set as an environment variable, e.g. export TF_VAR_grafana_access_token=<your_token>"
  type        = string
}

variable "lambda_runtime" {
  description = "The runtime of the Lambda function (e.g., python3.13)"
  type        = string
  default     = "python3.13"
}

variable "rotation_period_days" {
  description = "Number of days after which access keys should be rotated"
  type        = number
  default     = 30
}

variable "grafana_datasource_name" {
  description = "The name of the Grafana datasource"
  type        = string
  default     = "cw-demo-rotator-access-key"
}

variable "schedule_expression_iam_key_rotation" {
  description = "Schedule expression for the CloudWatch event for the iam key rotation"
  type        = string
  default     = "cron(0 8 * * ? *)"
}
