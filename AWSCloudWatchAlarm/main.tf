module "lambda_alarm_forwarder" {
  source        = "git::https://github.com/terraform-aws-modules/terraform-aws-lambda.git?ref=v6.4.0"
  function_name = "alarm-forwarder"
  description   = "alarm forwarder, forward alarm to cloudwatch metric"
  handler       = "lambda_function.lambda_handler"
  runtime       = var.lambda_runtime
  memory_size   = 160
  timeout       = 30
  source_path = [
    {
      path = "${path.module}/source-alarm-forwarder"
    }
  ]
  publish                           = true
  attach_policies                   = true
  attach_policy_jsons               = true
  number_of_policies                = 1
  number_of_policy_jsons            = 1
  policy_jsons                      = [data.template_file.lambda_policy_alarm_forwarder.rendered]
  policies                          = ["arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"]
  cloudwatch_logs_retention_in_days = 30
  create_lambda_function_url        = false
  allowed_triggers = {
    ScrappingRule = {
      principal    = "events.amazonaws.com"
      source_arn   = aws_cloudwatch_event_rule.scrapping_rule.arn
      statement_id = "AllowExecutionFromCloudWatch"
    }
  }
  environment_variables = {
    CLOUDWATCH_NAMESPACE = var.cloudwatch_namespace
  }
}

resource "aws_cloudwatch_event_rule" "scrapping_rule" {
  name                = "scrapping_rule"
  description         = "scrapping all lambdas in a single Account AWS"
  schedule_expression = var.schedule_expression_alarm_forwarder
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.scrapping_rule.name
  target_id = "SendToLambda"
  arn       = module.lambda_alarm_forwarder.lambda_function_arn
}

data "template_file" "lambda_policy_alarm_forwarder" {
  template = file("${path.module}/iam_policy_alarm_forwarder.json.tpl")
}
 