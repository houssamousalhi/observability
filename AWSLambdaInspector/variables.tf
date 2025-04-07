variable "lambda_versions" {
  description = "Map of environment, service, stack, and lambda function versions"
  type        = map(map(map(map(map(string)))))
  default = {
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
            "TerraformVersion" = "1.4.0-RC5"
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

variable "aws_region" {
  description = "The AWS region to deploy the resources in"
  type        = string
  default     = "us-east-1"
}

variable "schedule_expression" {
  description = "The schedule expression for the CloudWatch event"
  type        = string
  default     = "rate(5 minutes)"
}

variable "cloudwatch_namespace" {
  description = "The namespace for the CloudWatch metrics"
  type        = string
  default     = "LambdaInspect"
}

variable "grafana_url" {
  description = "The URL of the Grafana instance"
  type        = string
}

variable "grafana_access_token" {
  description = "The access token for the Grafana instance"
  type        = string
}
