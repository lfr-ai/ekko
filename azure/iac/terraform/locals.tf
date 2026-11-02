locals {
  # Environment-specific defaults
  resource_group_name = var.resource_group_name != "" ? var.resource_group_name : "${lower(var.project_name)}-${var.environment}-rg"
  base_name           = "${var.project_name}-${var.environment}"

  # Resolve environment-specific defaults
  log_retention_days = coalesce(
    var.log_retention_days,
    var.environment == "prod" ? 90 : 30
  )

  acr_sku = coalesce(
    var.acr_sku,
    var.environment == "prod" ? "Standard" : "Basic"
  )

  min_replicas = coalesce(
    var.min_replicas,
    var.environment == "prod" ? 1 : 0
  )

  max_replicas = coalesce(
    var.max_replicas,
    var.environment == "prod" ? 5 : 3
  )

  redis_sku_name = coalesce(
    var.redis_sku_name,
    var.environment == "prod" ? "Standard" : "Basic"
  )

  redis_sku_capacity = coalesce(
    var.redis_sku_capacity,
    var.environment == "prod" ? 1 : 0
  )

  public_network_access = coalesce(
    var.public_network_access,
    var.environment != "prod"
  )

  resource_group_tags = {
    project     = var.project_name
    environment = var.environment
    managedBy   = "terraform"
  }

  common_tags = {
    workload    = "ekko"
    environment = var.environment
    managedBy   = "terraform"
  }
}
