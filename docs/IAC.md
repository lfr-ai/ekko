# Infrastructure as Code (Azure Bicep)

This repository avoids using Azure Key Vault for secrets. Secrets should be provided via environment variables or Azure App Service/Container Apps configuration at deploy time.

Current IaC coverage (under `azure/iac`):
- ACR (container registry)
- Container App / Web App deployment
- Log Analytics
- Storage
- Cognitive Services (Azure OpenAI / Speech)

Key changes made:
- Removed Key Vault module and references. Secrets are injected via env or platform-managed secret stores.
- Kept `cognitiveServices.bicep` for Azure OpenAI / Speech resource provisioning.
