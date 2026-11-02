module "observability" {
  source = "./modules/log_analytics"

  resource_group_name   = azurerm_resource_group.main.name
  location              = azurerm_resource_group.main.location
  base_name             = local.base_name
  retention_in_days     = local.log_retention_days
  public_network_access = local.public_network_access
  tags                  = local.common_tags
}

module "registry" {
  source = "./modules/container_registry"

  resource_group_name   = azurerm_resource_group.main.name
  location              = azurerm_resource_group.main.location
  base_name             = local.base_name
  sku                   = local.acr_sku
  public_network_access = local.public_network_access
  tags                  = local.common_tags
}

module "container_environment" {
  source = "./modules/container_environment"

  resource_group_name        = azurerm_resource_group.main.name
  location                   = azurerm_resource_group.main.location
  base_name                  = local.base_name
  log_analytics_workspace_id = module.observability.workspace_id
  tags                       = local.common_tags
}

# Shared store for rate limiting and cross-replica transcript fan-out —
# required for correctness once the container app scales beyond one replica.
module "redis_cache" {
  source = "./modules/redis_cache"

  resource_group_name   = azurerm_resource_group.main.name
  location              = azurerm_resource_group.main.location
  base_name             = local.base_name
  sku_name              = local.redis_sku_name
  sku_family            = "C"
  sku_capacity          = local.redis_sku_capacity
  public_network_access = local.public_network_access
  tags                  = local.common_tags
}

module "container_app" {
  source = "./modules/container_app"

  resource_group_name            = azurerm_resource_group.main.name
  location                       = azurerm_resource_group.main.location
  base_name                      = local.base_name
  environment                    = var.environment
  container_app_environment_id   = module.container_environment.id
  acr_id                         = module.registry.id
  acr_name                       = module.registry.name
  acr_login_server               = module.registry.login_server
  image_name                     = var.image_name
  image_tag                      = var.image_tag
  image_digest                   = var.image_digest
  target_port                    = var.target_port
  min_replicas                   = local.min_replicas
  max_replicas                   = local.max_replicas
  cpu_cores                      = var.cpu_cores
  memory_gb                      = var.memory_gb
  app_insights_connection_string = module.observability.connection_string
  redis_hostname                 = module.redis_cache.hostname
  redis_name                     = module.redis_cache.name
  redis_ssl_port                 = module.redis_cache.ssl_port
  tags                           = local.common_tags
}
