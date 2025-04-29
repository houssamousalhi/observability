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
  name = var.grafana_datasource_name

  json_data_encoded = jsonencode({
    defaultRegion = var.aws_region
    authType      = "keys"
  })

  secure_json_data_encoded = jsonencode({
    accessKey = aws_iam_access_key.access_key.id
    secretKey = aws_iam_access_key.access_key.secret
  })
}


resource "grafana_dashboard" "cloudwatch_alarm" {
  config_json = templatefile("${path.module}/grafana/aws-cloudwatch-alarm.json.tpl", {
    cloudwatch_namespace = var.cloudwatch_namespace
  })
  overwrite = true
}

resource "grafana_contact_point" "default" {
  name = "default"

  email {
    addresses = [var.grafana_contact_point_email]
    message   = "{{ template \"default.message\" . }}"
    subject   = "{{ template \"default.title\" . }}"
  }
}

resource "grafana_notification_policy" "default" {
  contact_point   = grafana_contact_point.default.name
  group_by        = ["alertname"]
  group_wait      = "30s"
  group_interval  = "5m"
  repeat_interval = "4h"
}

# resource "grafana_rule_group" "cloudwatch_alarm" {
#   name             = "CloudWatch Alarm Monitor"
#   folder_uid       = "default"
#   interval_seconds = 60

#   rule {
#     name           = "CloudWatch Alarm Monitor"
#     condition      = "A"
#     no_data_state  = "NoData"
#     exec_err_state = "Error"

#     data {
#       ref_id = "A"
#       relative_time_range {
#         from = 900 # 15 minutes
#         to   = 0
#       }

#       datasource_uid = grafana_data_source.cloudwatch.uid

#       model = jsonencode({
#         alias = ""
#         datasource = {
#           uid = grafana_data_source.cloudwatch.uid
#         }
#         dimensions = {}
#         expression = ""
#         filters = [
#           {
#             key      = "AlarmState"
#             operator = "="
#             value    = "$status"
#           }
#         ]
#         id               = ""
#         instant          = false
#         intervalMs       = 1000
#         label            = "$${PROP(\"Dim.AlarmName\")} "
#         logGroups        = []
#         matchExact       = false
#         maxDataPoints    = 43200
#         metricEditorMode = 0
#         metricName       = "ActiveAlarm"
#         metricQueryType  = 0
#         namespace        = "CloudWatchAlarms"
#         period           = ""
#         queryLanguage    = "CWLI"
#         queryMode        = "Metrics"
#         range            = true
#         refId            = "A"
#         region           = var.aws_region
#         sqlExpression    = ""
#         statistic        = "Maximum"
#       })
#     }

#     for = "5m"
#     annotations = {
#       summary      = "CloudWatch Alarm is active"
#       description  = "A CloudWatch alarm has been triggered"
#       runbook_url  = "https://example.com/runbook/cloudwatch-alarms"
#       dashboardUid = "aws-cloudwatch-alarms"
#       panelId      = "2"
#       severity     = "critical"
#       environment  = "production"
#       service      = "cloudwatch"
#       alert_type   = "cloudwatch_alarm"
#     }
#     labels = {
#       severity = "critical"
#     }
#   }
# }
