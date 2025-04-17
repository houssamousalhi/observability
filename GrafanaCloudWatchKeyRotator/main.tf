locals {
  source_code_hash = sha256(join("", [
    for f in fileset("${path.module}/source", "**/*") : filesha256("${path.module}/source/${f}")
  ]))
  lambda_zip_path = "${path.module}/files/lambda_function.zip"
}

module "lambda_rotate_iam_keys" {
  source                            = "git::https://github.com/terraform-aws-modules/terraform-aws-lambda.git?ref=v6.4.0"
  function_name                     = "lbd-${var.environment}-grafana-cloudwatch-key-rotator"
  description                       = "rotate grafana cloudwatch key"
  handler                           = "grafana_cloudwatch_key_rotator.lambda_handler"
  runtime                           = var.lambda_runtime
  memory_size                       = 160
  timeout                           = 30
  create_package                    = false
  local_existing_package            = data.archive_file.lambda_zip.output_path
  publish                           = true
  attach_policies                   = true
  attach_policy_jsons               = true
  number_of_policies                = 1
  number_of_policy_jsons            = 1
  policy_jsons                      = [data.template_file.lambda_policy_rotate_iam_keys.rendered]
  policies                          = ["arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"]
  cloudwatch_logs_retention_in_days = 30
  create_lambda_function_url        = false
  environment_variables = {
    IAM_USERNAME            = aws_iam_user.grafana.name
    GRAFANA_API_KEY_PATH    = "grafana/apikey"
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
    aws_region = var.aws_region
    account_id = data.aws_caller_identity.current.account_id
    kms_key_id = aws_kms_key.cmk.key_id
  }
}

data "external" "build_lambda_package" {
  program = ["${path.module}/tf_wrapper.sh"]

  query = {
    source_code_hash = local.source_code_hash
    lambda_runtime   = var.lambda_runtime
    working_dir      = path.module
  }
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  output_path = local.lambda_zip_path
  source_dir  = "./files/temp/lambda_function/package"
  depends_on  = [data.external.build_lambda_package]
}