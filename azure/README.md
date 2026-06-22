# Azure Baseline (Ekko)

This folder provides a minimal Infrastructure-as-Code baseline for production-oriented Azure deployment patterns.

## Included

- `iac/main.bicep` — resource-group scoped baseline with Log Analytics + App Insights, tagged resources, and environment-aware observability posture
- `iac/main.parameters.json` — sample parameter file

### Key parameters

- `logAnalyticsRetentionInDays` (30-730)
- `logAnalyticsPublicNetworkAccess` (recommend `false` in production)
- `tags` object for consistent resource tagging
- `iac/appservice-acr.bicep` — App Service (Linux container) + ACR baseline for CI/CD deployment
- `iac/appservice-acr.parameters.json` — sample parameter file for App Service + ACR deployment

## Validation

- Validate Bicep before deployment:
  - `az bicep build --file azure/iac/main.bicep`
- Preview deployment changes before applying:
  - `az deployment group what-if --resource-group <rg-name> --template-file azure/iac/main.bicep --parameters @azure/iac/main.parameters.json`

## Deployment

- Resource-group deployment entrypoint:
  - `az deployment group create --resource-group <rg-name> --template-file azure/iac/main.bicep --parameters @azure/iac/main.parameters.json`

- App Service + ACR deployment entrypoint:
  - `az deployment group create --resource-group <rg-name> --template-file azure/iac/appservice-acr.bicep --parameters @azure/iac/appservice-acr.parameters.json`

After deployment, build and push your image to ACR (for example from CI), then
set `imageTag` in the parameter file (or override parameter at deploy time).

## Next steps

- Add workload-specific resources (Container Apps/App Service/AKS) as modules
- Configure environment-specific parameter files (`dev`, `test`, `prod`) and keep secrets in Key Vault (not in parameter JSON)
- Wire deployment into CI/CD after review
- Add policy/compliance checks (for example `azqr`) in CI before production rollout
- For production: set `logAnalyticsPublicNetworkAccess=false` and increase retention according to compliance policy
