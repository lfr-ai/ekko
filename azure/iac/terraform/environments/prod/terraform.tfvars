# ═══════════════════════════════════════════════════════════════
# Production Environment Terraform Variables
# ═══════════════════════════════════════════════════════════════
# This file configures the prod environment with production-grade
# resources, strict security settings, and immutable image digests.
#
# IMPORTANT: Images MUST be referenced by immutable sha256 digest,
# never by mutable tag (e.g., 'latest' or 'v1.2.3'). This ensures
# reproducible deployments and safe rollbacks.
#
# Image Digest Format: sha256:<64-hex-chars>
# Example: sha256:abc123def456...

subscription_id     = "REPLACE_WITH_PROD_SUBSCRIPTION_ID"
tenant_id           = "REPLACE_WITH_ENTRA_TENANT_ID"
location            = "swedencentral"
project_name        = "ekko"
environment         = "prod"
resource_group_name = "" # Defaults to ekko-prod-rg

# Container image: MUST be referenced by immutable digest (not tag)
# To get the digest, run: az acr repository show --name <acr> --image <image>:<tag> --query id
# Then extract the sha256 hash from the digest field.
# Example output: my-acr.azurecr.io/ekko@sha256:1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7a8b9c0d1e2f
#
# IMPORTANT: The value below is a PLACEHOLDER - replace with your ACTUAL image digest.
# Terraform will FAIL to deploy if you attempt to use the placeholder value below.
image_name   = "ekko"
image_tag    = ""                                                    # Ignored when image_digest is provided
image_digest = "PLACEHOLDER_INVALID_DIGEST_REPLACE_WITH_REAL_SHA256" # ⚠️  REPLACE with actual sha256 from ACR

# Observability: 90-day retention for prod
log_retention_days = 90

# Registry: Standard tier for prod (webhooks, advanced features)
acr_sku = "Standard"

# Scaling: 1-5 replicas for prod (always at least 1 running)
min_replicas = 1
max_replicas = 5

# Compute: 1 CPU, 2Gi memory per replica
cpu_cores   = 1
memory_gb   = "2Gi"
target_port = 8000

# Redis: Standard tier (1 replica, persistence, geo-replication capable)
redis_sku_name     = "Standard"
redis_sku_capacity = 1

# Public network access: disabled for prod (private endpoints/VNet only)
public_network_access = false

