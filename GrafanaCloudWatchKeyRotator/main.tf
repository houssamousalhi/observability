module "lambda_rotate_iam_keys" {
  source        = "git::https://github.com/terraform-aws-modules/terraform-aws-lambda.git?ref=v6.4.0"
  function_name = "lbd-${var.environment}-grafana-cloudwatch-key-rotator"
  description   = "rotate grafana cloudwatch key"
  handler       = "grafana_cloudwatch_key_rotator.lambda_handler"
  runtime       = var.lambda_runtime
  memory_size   = 160
  timeout       = 30
  source_path = [
    {
      path             = "${path.module}/source"
      pip_requirements = true
    }
  ]
  publish                           = true
  attach_policies                   = true
  attach_policy_jsons               = true
  number_of_policies                = 1
  number_of_policy_jsons            = 1
  policy_jsons                      = [data.template_file.lambda_policy_rotate_iam_keys.rendered]
  policies                          = ["arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"]
  cloudwatch_logs_retention_in_days = 30
  environment_variables = {
    IAM_USERNAME            = aws_iam_user.grafana.name
    GRAFANA_API_KEY_PATH    = aws_secretsmanager_secret.grafana_api_key.name
    GRAFANA_URL             = var.grafana_url
    GRAFANA_DATASOURCE_NAME = var.grafana_datasource_name
    ROTATION_PERIOD         = var.rotation_period_days
  }
  allowed_triggers = {
    DailyRotation = {
      principal    = "events.amazonaws.com"
      source_arn   = aws_cloudwatch_event_rule.iam_key_rotation.arn
      statement_id = "AllowExecutionFromCloudWatch"
    }
  }
}

# CloudWatch Event Rules
resource "aws_cloudwatch_event_rule" "iam_key_rotation" {
  name                = "iam_key_rotation_schedule"
  description         = "Schedule for IAM access key rotation"
  schedule_expression = var.schedule_expression_iam_key_rotation
}

# CloudWatch Event Targets
resource "aws_cloudwatch_event_target" "rotate_iam_keys_target" {
  rule      = aws_cloudwatch_event_rule.iam_key_rotation.name
  target_id = "SendToRotateIamKeys"
  arn       = module.lambda_rotate_iam_keys.lambda_function_arn
}

# IAM Policies
data "template_file" "lambda_policy_rotate_iam_keys" {
  template = file("${path.module}/iam_policy_rotate_iam_keys.json.tpl")
  vars = {
    aws_region                 = var.aws_region
    account_id                 = data.aws_caller_identity.current.account_id
    kms_key_id                 = aws_kms_key.cmk.key_id
    grafana_api_key_secret_arn = aws_secretsmanager_secret.grafana_api_key.arn
  }
}
