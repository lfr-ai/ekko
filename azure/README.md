# Azure Baseline (Ekko)

This folder provides a minimal Infrastructure-as-Code baseline for production-oriented Azure deployment patterns.

## Included

- `iac/main.bicep` — resource-group scoped baseline with Log Analytics and App Insights
- `iac/main.parameters.json` — sample parameter file

## Validation

- Validate Bicep before deployment:
  - `az bicep build --file azure/iac/main.bicep`
- Preview deployment changes before applying:
  - `az deployment group what-if --resource-group <rg-name> --template-file azure/iac/main.bicep --parameters @azure/iac/main.parameters.json`

## Deployment

- Resource-group deployment entrypoint:
  - `az deployment group create --resource-group <rg-name> --template-file azure/iac/main.bicep --parameters @azure/iac/main.parameters.json`

## Next steps

- Add workload-specific resources (Container Apps/App Service/AKS) as modules
- Configure environment-specific parameter files (`dev`, `test`, `prod`) and keep secrets in Key Vault (not in parameter JSON)
- Wire deployment into CI/CD after review
- Add policy/compliance checks (for example `azqr`) in CI before production rollout
