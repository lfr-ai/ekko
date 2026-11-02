# Bicep-to-Terraform Parity

Terraform mirrors the subscription-scoped resources in
[`../deploy.bicep`](../deploy.bicep) and the resource-group modules under
[`../modules/`](../modules/). This is a source comparison; Terraform has not
been applied and Bicep remains the deployment authority.

## Resource and environment matrix

| Area | Development | Production |
| --- | --- | --- |
| Resource group | `<project>-dev-rg` | `<project>-prod-rg` |
| Log Analytics retention | 30 days | 90 days |
| ACR SKU | Basic | Standard |
| Container App replicas | 0–3 | 1–5 |
| Redis SKU/capacity | Basic / 0 | Standard / 1 |
| Public ACR/Redis access | Enabled | Disabled |
| Container image | Mutable tag (default `latest`) | Required immutable SHA-256 digest |

The Terraform production digest requirement is intentionally stricter than the
current Bicep production parameter placeholder (`set-at-deploy`). Bicep is not
modified by this change.

Terraform resources use `managedBy = "terraform"` tags to distinguish ownership
from Bicep-managed resources.

## Container App

Both implementations configure a system-assigned identity with `AcrPull`,
external HTTPS ingress on the configured target port, a Redis connection secret,
and Application Insights connection settings. Terraform also expresses the
health checks (`/health`; liveness 15-second delay/30-second interval, readiness
10-second delay/15-second interval), HTTP concurrency scaling rule (`50`
requests), ingress client certificate mode (`Ignore`), and `auto` transport.

## Log Analytics and Container Apps environment

Terraform maps Bicep's environment-resolved Log Analytics public ingestion and
query settings to `internet_ingestion_enabled` and `internet_query_enabled`.
The Container Apps environment uses the same workspace through
`logs_destination = "log-analytics"`.

## Operational boundary

Development and production use separate Azure Blob backend example files and
state keys. Backend storage, OIDC identity, RBAC, and resource import/adoption
remain operator-managed. CI runs formatting, backend-free initialization,
validation, and TFLint only; it does not create plans or apply resources.
