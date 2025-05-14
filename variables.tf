variable "grafana_url" {
  description = "The URL of the Grafana instance"
  type        = string
}

variable "grafana_access_token" {
  description = "The access token for the Grafana instance"
  type        = string
}

variable "grafana_contact_point_email" {
  description = "The email address for the Grafana contact point"
  type        = string
  default     = ""
}

variable "grafana_contact_point_googlechat_url" {
  description = "The googlechat url for the Grafana contact point"
  type        = string
  default     = ""
}

variable "grafana_contact_point_slack_url" {
  description = "The slack url for the Grafana contact point"
  type        = string
  default     = ""
}
