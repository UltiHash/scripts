variable "aws_region" {
  description = "AWS region where the EKS cluster resides"
  type        = string
}

variable "registry_username" {
  type      = string
  sensitive = true
}

variable "registry_password" {
  type      = string
  sensitive = true
}

variable "ultihash_license" {
  description = "License to run UltiHash cluster"
  type        = string
  sensitive   = true
}

variable "monitoring_token" {
  description = "Token to push telemetry to the monitoring system"
  type        = string
  sensitive   = true
}

variable "helm_chart_installation_timeout" {
  description = "Time to install the UltiHash helm chart"
  type = number
}