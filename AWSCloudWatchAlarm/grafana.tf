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

resource "grafana_folder" "rule_folder" {
  title = "Alarms"
}

resource "grafana_dashboard" "cloudwatch_alarm" {
  config_json = templatefile("${path.module}/grafana/aws-cloudwatch-alarm.json.tpl", {
    cloudwatch_namespace = var.cloudwatch_namespace
  })
  folder    = grafana_folder.rule_folder.uid
  overwrite = true
}

resource "grafana_contact_point" "default" {
  name = "default"

  dynamic "email" {
    for_each = var.grafana_contact_point_email != "" ? [1] : []
    content {
      addresses = [var.grafana_contact_point_email]
      message   = "{{ template \"default.message\" . }}"
      subject   = "{{ template \"default.title\" . }}"
    }
  }

  dynamic "googlechat" {
    for_each = var.grafana_contact_point_googlechat_url != "" ? [1] : []
    content {
      url = var.grafana_contact_point_googlechat_url
    }
  }

  dynamic "slack" {
    for_each = var.grafana_contact_point_slack_url != "" ? [1] : []
    content {
      url = var.grafana_contact_point_slack_url
    }
  }
}

resource "grafana_notification_policy" "default" {
  contact_point   = grafana_contact_point.default.name
  group_by        = ["alertname"]
  group_wait      = "30s"
  group_interval  = "1m"
  repeat_interval = "4h"
}

resource "grafana_rule_group" "cloudwatch_alarm" {
  name             = "CloudWatch Alarms"
  folder_uid       = grafana_folder.rule_folder.uid
  interval_seconds = 60

  rule {
    name           = "CloudWatch Alarms"
    condition      = "C"
    no_data_state  = "OK"
    exec_err_state = "Error"

    data {
      ref_id = "A"
      relative_time_range {
        from = 60 # 1 minute
        to   = 0
      }
      datasource_uid = grafana_data_source.cloudwatch.uid
      model = jsonencode({
        alias = ""
        datasource = {
          uid = grafana_data_source.cloudwatch.uid
        }
        dimensions       = {}
        expression       = ""
        id               = ""
        instant          = true
        intervalMs       = 1000
        label            = "$${PROP(\"Dim.AlarmName\")}"
        logGroups        = []
        matchExact       = false
        maxDataPoints    = 1
        metricEditorMode = 0
        metricName       = "ActiveAlarm"
        metricQueryType  = 0
        namespace        = var.cloudwatch_namespace
        period           = "60"
        queryLanguage    = "CWLI"
        queryMode        = "Metrics"
        range            = false
        refId            = "A"
        region           = var.aws_region
        sqlExpression    = ""
        statistic        = "Maximum"
      })
    }

    data {
      ref_id = "B"
      relative_time_range {
        from = 0
        to   = 0
      }
      datasource_uid = "-100"
      model = jsonencode({
        type       = "reduce"
        reducer    = "last"
        expression = "A"
        refId      = "B"
        settings = {
          mode             = "replaceNN"
          replaceWithValue = 0
        }
      })
    }

    data {
      ref_id = "C"
      relative_time_range {
        from = 0
        to   = 0
      }
      datasource_uid = "-100"
      model = jsonencode({
        type = "threshold"
        conditions = [
          {
            evaluator = {
              params = [0]
              type   = "gt"
            }
          }
        ]
        expression = "B"
        refId      = "C"
      })
    }

    annotations = {
      description      = "A CloudWatch alarm has been triggered"
      __dashboardUid__ = grafana_dashboard.cloudwatch_alarm.uid
      __panelId__      = "2"
    }
  }
}
