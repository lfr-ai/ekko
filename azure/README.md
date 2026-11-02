# Azure deployment

Ekko's Bicep deployment provisions Azure Container Apps, Azure Container
Registry, Log Analytics/Application Insights, and Azure Cache for Redis.

## Entry points

- `iac/deploy.bicep` — subscription-scoped entry point; creates the resource
  group and deploys the workload.
- `iac/main.bicep` — resource-group-scoped workload modules.
- `iac/parameters/dev/deploy.dev.bicepparam` and
  `iac/parameters/prod/deploy.prod.bicepparam` — environment parameter files.
- `iac/modules/` — individual Azure resource modules.

The deployment entry point currently accepts `dev` and `prod`. Review the
environment parameters and resulting deployment preview before provisioning.

## Validate and preview

Build the subscription deployment template:

```powershell
az bicep build --file azure/iac/deploy.bicep
```

Preview a development deployment before applying it:

```powershell
az deployment sub what-if `
  --location swedencentral `
  --template-file azure/iac/deploy.bicep `
  --parameters azure/iac/parameters/dev/deploy.dev.bicepparam
```

Use the corresponding production parameter file only after reviewing the
environment-specific resource settings and cost/security impact. Deployment is
an operator action; see `azure/iac/` for the source of truth.

## Terraform mirror

`iac/terraform/` contains an AzureRM/HCL mirror for review and validation.
Bicep remains the deployment authority; Terraform CI performs static checks
only and does not plan or apply resources. See the
[Terraform guide](./iac/terraform/README.md) and
[parity matrix](./iac/terraform/PARITY_MATRIX.md).
