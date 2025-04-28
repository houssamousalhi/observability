# grafana
provider "grafana" {
  url  = var.grafana_url
  auth = var.grafana_access_token
}

# Define the IAM user
resource "aws_iam_user" "grafana" {
  name          = var.grafana_user_name
  force_destroy = true
}

# Attach CloudWatchReadOnlyAccess policy to the IAM user
resource "aws_iam_user_policy_attachment" "cloudwatch_policy" {
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchReadOnlyAccess"
  user       = aws_iam_user.grafana.name
}

# new datasource cw
resource "grafana_data_source" "cloudwatch" {
  type = "cloudwatch"
  name = var.grafana_datasource_name

  json_data_encoded = jsonencode({
    defaultRegion = var.aws_region
    authType      = "keys"
  })

  # We don't set the access key here as it will be managed by the Lambda function
  secure_json_data_encoded = jsonencode({
    accessKey = "" # Will be updated by Lambda
    secretKey = "" # Will be updated by Lambda
  })
}

resource "aws_secretsmanager_secret" "grafana_api_key" {
  name                    = "grafana/apikey"
  description             = "Grafana API key"
  kms_key_id              = aws_kms_key.cmk.key_id
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "grafana_api_key_version" {
  secret_id     = aws_secretsmanager_secret.grafana_api_key.id
  secret_string = jsonencode({ "apikey" = var.grafana_access_token })
}
