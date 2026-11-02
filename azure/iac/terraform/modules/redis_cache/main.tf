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

variable "sku_name" {
  type        = string
  description = "Redis cache SKU tier (Basic or Standard)"
  default     = "Basic"

  validation {
    condition     = contains(["Basic", "Standard", "Premium"], var.sku_name)
    error_message = "SKU must be Basic, Standard, or Premium."
  }
}

variable "sku_family" {
  type        = string
  description = "Redis cache SKU family"
  default     = "C"

  validation {
    condition     = contains(["C", "P"], var.sku_family)
    error_message = "SKU family must be C (Basic/Standard) or P (Premium)."
  }
}

variable "sku_capacity" {
  type        = number
  description = "Redis cache SKU capacity (0-6 for family C, 1-5 for family P)"
  default     = 0

  validation {
    condition     = var.sku_capacity >= 0 && var.sku_capacity <= 6
    error_message = "SKU capacity must be between 0 and 6."
  }
}

variable "public_network_access" {
  type        = bool
  description = "Allow public network access to Redis"
  default     = true
}

variable "tags" {
  type        = map(string)
  description = "Tags to apply to resources"
  default     = {}
}

resource "azurerm_redis_cache" "main" {
  name                = "${var.base_name}-redis"
  resource_group_name = var.resource_group_name
  location            = var.location
  capacity            = var.sku_capacity
  family              = var.sku_family
  sku_name            = var.sku_name

  minimum_tls_version           = "1.2"
  public_network_access_enabled = var.public_network_access

  tags = var.tags
}

output "id" {
  value       = azurerm_redis_cache.main.id
  description = "Azure Cache for Redis resource ID"
}

output "name" {
  value       = azurerm_redis_cache.main.name
  description = "Azure Cache for Redis name"
}

output "hostname" {
  value       = azurerm_redis_cache.main.hostname
  description = "Azure Cache for Redis hostname"
}

output "ssl_port" {
  value       = azurerm_redis_cache.main.ssl_port
  description = "Azure Cache for Redis SSL port"
}

# Note: Primary connection string with auth key is sensitive and not exposed
# Use Azure SDK or Portal to retrieve at runtime when needed
