output "resource_group_name" {
  value       = azurerm_resource_group.main.name
  description = "Resource group name"
}

output "resource_group_id" {
  value       = azurerm_resource_group.main.id
  description = "Resource group resource ID"
}

output "log_analytics_workspace_id" {
  value       = module.observability.workspace_id
  description = "Log Analytics workspace resource ID"
}

output "application_insights_connection_string" {
  value       = module.observability.connection_string
  sensitive   = true
  description = "Application Insights connection string"
}

output "container_apps_environment_id" {
  value       = module.container_environment.id
  description = "Container Apps environment resource ID"
}

output "container_app_name" {
  value       = module.container_app.name
  description = "Container app name"
}

output "container_app_fqdn" {
  value       = module.container_app.fqdn
  description = "Container app fully qualified domain name"
}

output "acr_login_server" {
  value       = module.registry.login_server
  description = "Azure Container Registry login server"
}

output "redis_hostname" {
  value       = module.redis_cache.hostname
  description = "Azure Cache for Redis hostname"
}

# Note: Redis credentials (primary key) are sensitive and retrieved at runtime.
# Use 'az redis list-keys' or Azure Portal to access when needed.
# DO NOT export primary keys in outputs or state files.
