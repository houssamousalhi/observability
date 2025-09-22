module "cloudwatch_alarm" {
  source                               = "./AWSCloudWatchAlarm"
  grafana_url                          = var.grafana_url
  grafana_access_token                 = var.grafana_access_token
  schedule_expression_alarm_forwarder  = "rate(1 hour)"
  grafana_contact_point_email          = var.grafana_contact_point_email
  grafana_contact_point_googlechat_url = var.grafana_contact_point_googlechat_url
  grafana_contact_point_slack_url      = var.grafana_contact_point_slack_url
}
module "lambda_inspector" {
  source                               = "./AWSLambdaInspector"
  grafana_url                          = var.grafana_url
  grafana_access_token                 = var.grafana_access_token
  schedule_expression_lambda_inspector = "rate(5 minutes)"
  lambda_versions = {
    "prod" = {
      "primary" = {
        "frontend" = {
          "auth" = {
            "version"          = "1.2.0"
            "TerraformVersion" = "1.3.0-RELEASE"
          }
          "cache" = {
            "version"          = "2.4.0"
            "TerraformVersion" = "1.3.0-RELEASE"
          }
        }
        "backend" = {
          "producer" = {
            "version"          = "1.2.0"
            "TerraformVersion" = "1.4.0-RELEASE"
          }
          "consumer" = {
            "version"          = "2.5.0"
            "TerraformVersion" = "1.4.0-RELEASE"
          }
        }
      }
      "next" = {
        "frontend" = {
          "auth" = {
            "version"          = "1.2.0"
            "TerraformVersion" = "1.3.0-RELEASE"
          }
          "cache" = {
            "version"          = "2.4.0"
            "TerraformVersion" = "1.3.0-RELEASE"
          }
        }
        "backend" = {
          "producer" = {
            "version"          = "1.1.1"
            "TerraformVersion" = "1.4.0-RC6"
          }
          "consumer" = {
            "version"          = "2.4.1"
            "TerraformVersion" = "1.4.0-RC5"
          }
        }
      }
    }
    "dev" = {
      "primary" = {
        "frontend" = {
          "auth" = {
            "version"          = "1.2.0"
            "TerraformVersion" = "1.4.0-SNAPSHOT"
          }
          "cache" = {
            "version"          = "2.4.0"
            "TerraformVersion" = "1.4.0-SNAPSHOT"
          }
        }
        "backend" = {
          "producer" = {
            "version"          = "1.1.1"
            "TerraformVersion" = "1.4.0-RC6"
          }
          "consumer" = {
            "version"          = "2.4.1"
            "TerraformVersion" = "1.4.0-RC5"
          }
        }
      }
    }
  }
}

module "grafana_cloudwatch_key_rotator" {
  source               = "./GrafanaCloudWatchKeyRotator"
  grafana_url          = var.grafana_url
  grafana_access_token = var.grafana_access_token
}
