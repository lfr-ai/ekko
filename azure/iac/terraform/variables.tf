variable "subscription_id" {
  type        = string
  description = "Azure subscription ID"
}

variable "tenant_id" {
  type        = string
  description = "Azure Entra tenant ID"
}

variable "location" {
  type        = string
  description = "Azure region for all resources"
  default     = "swedencentral"
}

variable "project_name" {
  type        = string
  description = "Project name used for resource naming (2-12 characters)"
  default     = "ekko"

  validation {
    condition     = length(var.project_name) >= 2 && length(var.project_name) <= 12
    error_message = "Project name must be 2-12 characters."
  }
}

variable "environment" {
  type        = string
  description = "Deployment environment"

  validation {
    condition     = contains(["dev", "prod"], var.environment)
    error_message = "Environment must be 'dev' or 'prod'."
  }
}

variable "resource_group_name" {
  type        = string
  description = "Optional resource group name override. Defaults to {project}-{env}-rg."
  default     = ""
}

variable "image_name" {
  type        = string
  description = "Container image name inside ACR repository"
  default     = "ekko"
}

variable "image_tag" {
  type        = string
  description = "Container image tag to deploy. Used for tag-based image references (e.g., 'latest', 'v1.2.3'). If image_digest is provided, this is ignored."
  default     = "latest"
}

variable "image_digest" {
  type        = string
  description = "Container image digest (sha256 hash) for immutable references. Format: 'sha256:<64-hex-chars>'. When provided, overrides image_tag. Recommended for production deployments."
  default     = null

  validation {
    condition     = var.image_digest == null || can(regex("^sha256:[a-f0-9]{64}$", var.image_digest))
    error_message = "image_digest must be null or match 'sha256:<64-hex-chars>' format."
  }

  validation {
    condition     = var.image_digest == null || var.image_digest != "PLACEHOLDER_INVALID_DIGEST_REPLACE_WITH_REAL_SHA256"
    error_message = "ERROR: image_digest is still set to placeholder 'PLACEHOLDER_INVALID_DIGEST_REPLACE_WITH_REAL_SHA256'. Replace with actual sha256 from ACR: sha256:<64-hex>."
  }

  validation {
    condition     = var.image_digest == null || var.image_digest != "sha256:0000000000000000000000000000000000000000000000000000000000000000"
    error_message = "ERROR: image_digest is set to all-zero placeholder. Replace with actual sha256 from ACR: sha256:<64-hex>."
  }

  validation {
    condition     = var.environment != "prod" || var.image_digest != null
    error_message = "ERROR: Production deployments (environment=prod) REQUIRE a real, immutable image digest. Set image_digest to actual sha256 from ACR: sha256:<64-hex>. Do not use null/default in production."
  }
}

# Log Analytics retention: dev 30 days, prod 90 days
variable "log_retention_days" {
  type        = number
  description = "Log Analytics workspace retention in days"
  default     = null # Determined by environment
}

# ACR SKU: dev Basic, prod Standard
variable "acr_sku" {
  type        = string
  description = "Azure Container Registry SKU"
  default     = null # Determined by environment

  validation {
    condition     = var.acr_sku == null || contains(["Basic", "Standard", "Premium"], var.acr_sku)
    error_message = "ACR SKU must be Basic, Standard, or Premium."
  }
}

# Container App scaling: dev 0-3 replicas, prod 1-5 replicas
variable "min_replicas" {
  type        = number
  description = "Minimum number of container app replicas"
  default     = null # Determined by environment
}

variable "max_replicas" {
  type        = number
  description = "Maximum number of container app replicas"
  default     = null # Determined by environment
}

# Container App resources
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

variable "target_port" {
  type        = number
  description = "Container app ingress target port"
  default     = 8000
}

# Redis SKU: dev Basic/0, prod Standard/1
variable "redis_sku_name" {
  type        = string
  description = "Redis cache SKU tier (Basic or Standard)"
  default     = null # Determined by environment

  validation {
    condition     = var.redis_sku_name == null || contains(["Basic", "Standard", "Premium"], var.redis_sku_name)
    error_message = "Redis SKU must be Basic, Standard, or Premium."
  }
}

variable "redis_sku_capacity" {
  type        = number
  description = "Redis cache SKU capacity (0-6 for family C, 1-5 for family P)"
  default     = null # Determined by environment
}

# Public network access: enabled for dev, disabled for prod
variable "public_network_access" {
  type        = bool
  description = "Allow public network access for ACR and Redis"
  default     = null # Determined by environment
}
