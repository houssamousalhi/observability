terraform {
  required_version = ">= 1.0.11"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.59.0"
    }
    template = {
      source  = "hashicorp/template"
      version = "~> 2"
    }
    grafana = {
      source  = "grafana/grafana"
      version = "~> 3.22.0"
    }
  }
}
