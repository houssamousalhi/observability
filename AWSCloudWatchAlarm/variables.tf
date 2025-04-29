variable "aws_region" {
  description = "The AWS region to deploy the resources in"
  type        = string
  default     = "us-east-1"
}

variable "lambda_runtime" {
  description = "The runtime of the Lambda function (e.g., python3.13)"
  type        = string
  default     = "python3.13"
}

variable "schedule_expression_alarm_forwarder" {
  description = "The schedule expression for the CloudWatch event"
  type        = string
  default     = "rate(5 minutes)"
}

variable "cloudwatch_namespace" {
  description = "The namespace for the CloudWatch metrics"
  type        = string
  default     = "CloudWatchAlarmsDemo"
}

variable "grafana_url" {
  description = "The URL of the Grafana instance"
  type        = string
}

variable "grafana_access_token" {
  description = "The access token for the Grafana instance, can be found in the Grafana UI under the user menu > API keys, can be stored in the terraform.auto.tfvars file, or set as an environment variable, e.g. export TF_VAR_grafana_access_token=<your_token>"
  type        = string
}

variable "grafana_datasource_name" {
  description = "The name of the Grafana datasource"
  type        = string
  default     = "cw-alarm-demo"
}

variable "grafana_user_name" {
  description = "The name of the Grafana user"
  type        = string
  default     = "grafana-cloudwatch-alarm-demo"
}

variable "grafana_contact_point_email" {
  description = "The email address for the Grafana contact point"
  type        = string
}
