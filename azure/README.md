Azure infrastructure for the voice-bot project

This folder previously contained a full set of Bicep modules. To simplify the
repository and remove accidental dependency on Azure Key Vault, the default
deployment templates have been reduced to a minimal set focused on provisioning
only the resources we currently maintain in IaC here:

- OpenAI / ChatGPT endpoint wiring (where applicable)
- Speech-to-text (STT) compute / storage scaffolding

For other cloud infrastructure (ACR, container apps, monitoring) prefer using
the organization's centralized IaC repository or add explicit modules in a
separate workstream. Secrets should be provided via environment variables or
an external secrets manager (not Key Vault) unless explicitly enabled.

Usage

1. Edit `parameters/{env}.json` with appropriate names and values.
2. Deploy with:

```bash
az deployment group create \
  --resource-group my-rg \
  --template-file azure/iac/main.bicep \
  --parameters @azure/iac/parameters/dev.parameters.json
```

Or run the included `deploy.sh` / `deploy.ps1` scripts.
