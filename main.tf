module "cloudwatch_alarm" {
  source                              = "./AWSCloudWatchAlarm"
  grafana_url                         = var.grafana_url
  grafana_access_token                = var.grafana_access_token
  schedule_expression_alarm_forwarder = "rate(60 minutes)"
}
module "lambda_inspector" {
  source                               = "./AWSLambdaInspector"
  grafana_url                          = var.grafana_url
  grafana_access_token                 = var.grafana_access_token
  schedule_expression_lambda_inspector = "rate(60 minutes)"
}
module "grafana_cloudwatch_key_rotator" {
  source               = "./GrafanaCloudWatchKeyRotator"
  grafana_url          = var.grafana_url
  grafana_access_token = var.grafana_access_token
}
