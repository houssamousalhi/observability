module "cloudwatch_alarm" {
  source                              = "./AWSCloudWatchAlarm"
  grafana_url                         = var.grafana_url
  grafana_access_token                = var.grafana_access_token
  schedule_expression_alarm_forwarder = "rate(1 minute)"
  grafana_contact_point_email         = var.grafana_contact_point_email
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
