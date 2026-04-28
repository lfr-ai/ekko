# Deployment notes

This repository contains lightweight infrastructure templates under `azure/iac/`.
Per current policy, Key Vault is not used; secrets must be supplied via environment
mechanisms in CI or container orchestrator secret stores.

The `cognitiveServices` module remains and can be used to deploy an Azure
OpenAI/Cognitive resource if desired. Bicep templates are intentionally minimal
and should be parameterized for production usage.

If you prefer not to use Azure at all, the app runs locally with environment
variables and a local Postgres instance.
