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

variable "retention_in_days" {
  type        = number
  description = "Log Analytics retention in days"
  default     = 30
}

variable "public_network_access" {
  type        = bool
  description = "Allow public network access to Log Analytics (ingestion and query)"
  default     = true
}

variable "tags" {
  type        = map(string)
  description = "Tags to apply to resources"
  default     = {}
}

resource "azurerm_log_analytics_workspace" "main" {
  name                       = "${var.base_name}-law"
  location                   = var.location
  resource_group_name        = var.resource_group_name
  sku                        = "PerGB2018"
  retention_in_days          = var.retention_in_days
  internet_ingestion_enabled = var.public_network_access
  internet_query_enabled     = var.public_network_access

  tags = var.tags
}

resource "azurerm_application_insights" "main" {
  name                = "${var.base_name}-appi"
  location            = var.location
  resource_group_name = var.resource_group_name
  application_type    = "web"
  workspace_id        = azurerm_log_analytics_workspace.main.id

  tags = var.tags

  depends_on = [azurerm_log_analytics_workspace.main]
}

output "workspace_id" {
  value       = azurerm_log_analytics_workspace.main.id
  description = "Log Analytics workspace resource ID"
}

output "connection_string" {
  value       = azurerm_application_insights.main.connection_string
  sensitive   = true
  description = "Application Insights connection string"
}
