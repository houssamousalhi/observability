module "lambda_app_inspector" {
  source                            = "git::https://github.com/terraform-aws-modules/terraform-aws-lambda.git?ref=v6.4.0"
  function_name                     = "app-inspector"
  description                       = "app inspector, push lambda and terraform tags to cloudwatch metric"
  handler                           = "lambda_function.lambda_handler"
  runtime                           = "python3.13"
  memory_size                       = 160
  timeout                           = 30
  create_package                    = false
  local_existing_package            = data.archive_file.app-inspector.output_path
  publish                           = true
  attach_policies                   = true
  attach_policy_jsons               = true
  number_of_policies                = 1
  number_of_policy_jsons            = 1
  policy_jsons                      = [data.template_file.lambda_policy_app_inspector.rendered]
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
}

resource "aws_cloudwatch_event_rule" "scrapping_rule" {
  name                = "scrapping_rule"
  description         = "scrapping all lambdas in a single Account AWS"
  schedule_expression = "rate(5 minutes)"
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.scrapping_rule.name
  target_id = "SendToLambda"
  arn       = module.lambda_app_inspector.lambda_function_arn
}

data "template_file" "lambda_policy_app_inspector" {
  template = file("${path.module}/iam_policy_app_inspector.json.tpl")
}

data "archive_file" "app-inspector" {
  type        = "zip"
  source_dir  = "${path.module}/lambda_source"
  output_path = "./files/app-inspector.zip"
}