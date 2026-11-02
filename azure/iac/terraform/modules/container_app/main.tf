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

variable "environment" {
  type        = string
  description = "Deployment environment"
}

variable "container_app_environment_id" {
  type        = string
  description = "Container Apps environment resource ID"
}

variable "acr_id" {
  type        = string
  description = "Azure Container Registry resource ID"
}

variable "acr_name" {
  type        = string
  description = "Azure Container Registry name"
}

variable "acr_login_server" {
  type        = string
  description = "Azure Container Registry login server"
}

variable "image_name" {
  type        = string
  description = "Container image name inside ACR repository"
  default     = "ekko"
}

variable "image_tag" {
  type        = string
  description = "Container image tag to deploy. Used for tag-based references (e.g., 'latest', 'v1.2.3'). Ignored if image_digest is provided."
  default     = "latest"
}

variable "image_digest" {
  type        = string
  description = "Container image digest (sha256 hash) for immutable references. Format: 'sha256:<64-hex-chars>'. Overrides image_tag when provided. Recommended for production."
  default     = null

  validation {
    condition     = var.image_digest == null || can(regex("^sha256:[a-f0-9]{64}$", var.image_digest))
    error_message = "image_digest must be null or match 'sha256:<64-hex-chars>' format."
  }
}

variable "target_port" {
  type        = number
  description = "Container app ingress target port"
  default     = 8000
}

variable "min_replicas" {
  type        = number
  description = "Minimum number of container app replicas"
  default     = 0
}

variable "max_replicas" {
  type        = number
  description = "Maximum number of container app replicas"
  default     = 3
}

variable "cpu_cores" {
  type        = number
  description = "CPU allocation per container app replica"
  default     = 1
}

variable "memory_gb" {
  type        = string
  description = "Memory allocation per container app replica in Gi"
  default     = "2Gi"
}

variable "app_insights_connection_string" {
  type        = string
  description = "Application Insights connection string"
  sensitive   = true
}

variable "redis_hostname" {
  type        = string
  description = "Azure Cache for Redis hostname"
}

variable "redis_name" {
  type        = string
  description = "Azure Cache for Redis name"
}

variable "redis_ssl_port" {
  type        = number
  description = "Azure Cache for Redis SSL port"
  default     = 6380
}

variable "tags" {
  type        = map(string)
  description = "Tags to apply to resources"
  default     = {}
}

locals {
  container_app_name = "${var.base_name}-ca"
  # Image reference: use digest if provided (immutable), otherwise use tag
  image_ref = var.image_digest != null ? "${var.acr_login_server}/${var.image_name}@${var.image_digest}" : "${var.acr_login_server}/${var.image_name}:${var.image_tag}"
}

# Reference the Redis cache to retrieve the primary key
data "azurerm_redis_cache" "main" {
  name                = var.redis_name
  resource_group_name = var.resource_group_name
}

# Reference the ACR for role assignment
data "azurerm_container_registry" "main" {
  name                = var.acr_name
  resource_group_name = var.resource_group_name
}

resource "azurerm_container_app" "main" {
  name                         = local.container_app_name
  container_app_environment_id = var.container_app_environment_id
  resource_group_name          = var.resource_group_name
  revision_mode                = "Single"

  template {
    container {
      name   = "ekko"
      image  = local.image_ref
      cpu    = var.cpu_cores
      memory = var.memory_gb

      env {
        name  = "EKKO_ENVIRONMENT"
        value = var.environment
      }

      env {
        name  = "APPLICATIONINSIGHTS_CONNECTION_STRING"
        value = var.app_insights_connection_string
      }

      env {
        name        = "EKKO_REDIS_URL"
        secret_name = "redis-connection-string"
      }

      # Liveness probe: detects if container is alive (Bicep parity)
      # Sends HTTP GET request to /health every 30s after 15s initial delay
      liveness_probe {
        transport        = "HTTP"
        port             = var.target_port
        path             = "/health"
        initial_delay    = 15
        interval_seconds = 30
      }

      # Readiness probe: detects if container is ready to receive traffic (Bicep parity)
      # Sends HTTP GET request to /health every 15s after 10s initial delay
      readiness_probe {
        transport        = "HTTP"
        port             = var.target_port
        path             = "/health"
        initial_delay    = 10
        interval_seconds = 15
      }
    }

    min_replicas = var.min_replicas
    max_replicas = var.max_replicas

    # HTTP concurrency scaling rule (Bicep parity: matches concurrentRequests: 50)
    # Scales based on concurrent HTTP requests per container
    http_scale_rule {
      name                = "http-concurrency"
      concurrent_requests = "50"
    }
  }

  ingress {
    allow_insecure_connections = false
    client_certificate_mode    = "ignore"
    external_enabled           = true
    target_port                = var.target_port
    transport                  = "auto"
    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  # Use system-assigned managed identity with ACR system identity auth (Bicep parity).
  # Bicep: registries[0].identity: 'system'
  registry {
    server   = var.acr_login_server
    identity = "system"
  }

  secret {
    name  = "redis-connection-string"
    value = "rediss://:${data.azurerm_redis_cache.main.primary_access_key}@${var.redis_hostname}:${var.redis_ssl_port}/0"
  }

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

# Grant the container app's system-assigned identity AcrPull role on the ACR
resource "azurerm_role_assignment" "acr_pull" {
  scope              = data.azurerm_container_registry.main.id
  role_definition_id = "/subscriptions/${data.azurerm_client_config.current.subscription_id}/providers/Microsoft.Authorization/roleDefinitions/7f951dda-4ed3-4680-a7ca-43fe172d538d"
  principal_id       = azurerm_container_app.main.identity[0].principal_id
  principal_type     = "ServicePrincipal"
}

data "azurerm_client_config" "current" {}

output "name" {
  value       = azurerm_container_app.main.name
  description = "Container app name"
}

output "fqdn" {
  value       = azurerm_container_app.main.ingress[0].fqdn
  description = "Container app fully qualified domain name"
}

output "acr_pull_role_assignment_id" {
  value       = azurerm_role_assignment.acr_pull.id
  description = "ACR pull role assignment resource ID"
}
