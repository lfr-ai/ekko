terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

variable "resource_group_name" {
  type        = string
  description = "Resource group name"
}

variable "location" {
  type        = string
  description = "Azure region"
}

variable "base_name" {
  type        = string
  description = "Base name for resources"
}

variable "log_analytics_workspace_id" {
  type        = string
  description = "Log Analytics workspace resource ID"
}

variable "tags" {
  type        = map(string)
  description = "Tags to apply to resources"
  default     = {}
}

resource "azurerm_container_app_environment" "main" {
  name                       = "${var.base_name}-cae"
  resource_group_name        = var.resource_group_name
  location                   = var.location
  logs_destination           = "log-analytics"
  log_analytics_workspace_id = var.log_analytics_workspace_id

  tags = var.tags
}

output "id" {
  value       = azurerm_container_app_environment.main.id
  description = "Container Apps environment resource ID"
}

output "name" {
  value       = azurerm_container_app_environment.main.name
  description = "Container Apps environment name"
}
