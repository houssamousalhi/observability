locals {
  flattened_lambdas = {
    for key in flatten([
      for env, stacks in var.lambda_versions : [
        for stack, services in stacks : [
          for service, lambdas in services : [
            for lambda, config in lambdas : {
              key = "${env}-${stack}-${service}-${lambda}"
              value = {
                env              = env
                service          = service
                stack            = stack
                lambda           = lambda
                version          = config.version
                TerraformVersion = config.TerraformVersion
              }
            }
          ]
        ]
      ]
    ]) : key.key => key.value
  }
}

module "lambda_example" {
  for_each                          = local.flattened_lambdas
  source                            = "git::https://github.com/terraform-aws-modules/terraform-aws-lambda.git?ref=v6.4.0"
  function_name                     = "lbd-${each.value.env}-${each.value.service}-${each.value.stack}-${each.value.lambda}"
  description                       = "example to track the lambda tags"
  handler                           = "lambda_function.lambda_handler"
  runtime                           = "python3.13"
  memory_size                       = 160
  timeout                           = 30
  create_package                    = false
  local_existing_package            = data.archive_file.example.output_path
  publish                           = true
  attach_policies                   = true
  attach_policy_jsons               = true
  number_of_policies                = 1
  policies                          = ["arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"]
  cloudwatch_logs_retention_in_days = 30
  create_lambda_function_url        = false
  function_tags = {
    "Environment"      = each.value.env
    "AppVersion"       = each.value.version
    "Stack"            = each.value.stack
    "Service"          = each.value.service
    "TerraformVersion" = each.value.TerraformVersion
  }
}

data "archive_file" "example" {
  type        = "zip"
  source_dir  = "${path.module}/source-example"
  output_path = "./files/example.zip"
}

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
  environment_variables = {
    CLOUDWATCH_NAMESPACE = var.cloudwatch_namespace
  }
}

resource "aws_cloudwatch_event_rule" "scrapping_rule" {
  name                = "scrapping_rule"
  description         = "scrapping all lambdas in a single Account AWS"
  schedule_expression = var.schedule_expression
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
  source_dir  = "${path.module}/source-inspector"
  output_path = "./files/app-inspector.zip"
}