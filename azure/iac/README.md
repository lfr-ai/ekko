Azure IaC for voice-bot

This folder contains Bicep modules and a top-level `main.bicep` to deploy the minimal infrastructure required to run the backend service in Azure.

Included modules (Key Vault is optional and disabled by default):
- Log Analytics workspace
- Azure Container Registry
- App Service Plan
- Web App (Linux single-container)
- Storage Account
- Cognitive Services (placeholder for Azure OpenAI / Cognitive account)

Usage (az cli):

```bash
az deployment group create --resource-group <rg> --template-file azure/iac/main.bicep --parameters containerImage=<acrLoginServer>/myimage:tag
```

Notes:
- This is a starting scaffold modeled after your golden-standard repos. Validate the Azure OpenAI/Cognitive resource requirements for your region and subscription before deploying.
- Secrets are not stored in Key Vault by default; provide them via environment variables or platform-managed secret stores. If you choose to enable Key Vault, add Role Assignments, Key Vault access policies and Managed Identity wiring as part of a separate workstream.
