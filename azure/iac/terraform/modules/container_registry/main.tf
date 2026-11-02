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

variable "sku" {
  type        = string
  description = "Azure Container Registry SKU"
  default     = "Basic"

  validation {
    condition     = contains(["Basic", "Standard", "Premium"], var.sku)
    error_message = "SKU must be Basic, Standard, or Premium."
  }
}

variable "public_network_access" {
  type        = bool
  description = "Allow public network access to ACR"
  default     = true
}

variable "tags" {
  type        = map(string)
  description = "Tags to apply to resources"
  default     = {}
}

resource "azurerm_container_registry" "main" {
  name                = lower(replace("${var.base_name}acr", "-", ""))
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = var.sku

  admin_enabled                 = false
  public_network_access_enabled = var.public_network_access

  tags = var.tags
}

output "id" {
  value       = azurerm_container_registry.main.id
  description = "Azure Container Registry resource ID"
}

output "name" {
  value       = azurerm_container_registry.main.name
  description = "Azure Container Registry name"
}

output "login_server" {
  value       = azurerm_container_registry.main.login_server
  description = "Azure Container Registry login server"
}
