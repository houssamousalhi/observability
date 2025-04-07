# grafana
provider "grafana" {
  url  = var.grafana_url
  auth = var.grafana_access_token
}

# Define the IAM user
resource "aws_iam_user" "grafana" {
  name = "grafana"
}

# Attach the IAM access key to the user
resource "aws_iam_access_key" "access_key" {
  user = aws_iam_user.grafana.name
}

# Attach CloudWatchReadOnlyAccess policy to the IAM user
resource "aws_iam_user_policy_attachment" "cloudwatch_policy" {
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchReadOnlyAccess"
  user       = aws_iam_user.grafana.name
}

# new datasource cw
resource "grafana_data_source" "cloudwatch" {
  type = "cloudwatch"
  name = "cw"

  json_data_encoded = jsonencode({
    defaultRegion = var.aws_region
    authType      = "keys"
  })

  secure_json_data_encoded = jsonencode({
    accessKey = aws_iam_access_key.access_key.id
    secretKey = aws_iam_access_key.access_key.secret
  })
}


resource "grafana_dashboard" "lambda_inspector" {
  config_json = templatefile("${path.module}/grafana-dashboard/aws-lambda-inspector-cloudwatch.json.tpl", {
    cloudwatch_namespace = var.cloudwatch_namespace
  })
}