# ═══════════════════════════════════════════════════════════════
# Development Environment Terraform Variables
# ═══════════════════════════════════════════════════════════════
# This file configures the dev environment with minimal resources
# and public network access enabled for developer convenience.

subscription_id     = "REPLACE_WITH_DEV_SUBSCRIPTION_ID"
tenant_id           = "REPLACE_WITH_ENTRA_TENANT_ID"
location            = "swedencentral"
project_name        = "ekko"
environment         = "dev"
resource_group_name = "" # Defaults to ekko-dev-rg

# Container image: dev uses mutable tags for rapid iteration
# image_tag: can be any tag (default 'latest')
# image_digest: optional; if provided, overrides image_tag
image_name   = "ekko"
image_tag    = "latest" # Dev allows mutable tags for rapid iteration
image_digest = null     # Dev doesn't require digest; leave null

# Observability: 30-day retention for dev
log_retention_days = 30

# Registry: Basic tier for dev (limited features, lower cost)
acr_sku = "Basic"

# Scaling: 0-3 replicas for dev (auto-scale from zero)
min_replicas = 0
max_replicas = 3

# Compute: 1 CPU, 2Gi memory per replica
cpu_cores   = 1
memory_gb   = "2Gi"
target_port = 8000

# Redis: Basic tier (0 replicas, single node, in-memory only)
redis_sku_name     = "Basic"
redis_sku_capacity = 0

# Public network access: enabled for dev
public_network_access = true

