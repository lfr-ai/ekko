# Design: Golden standard platform alignment

## Architecture impact

This change is infrastructure/configuration-centric and preserves existing Clean Architecture dependencies.

- Application and domain code are not re-layered.
- New observability files live under `docker/observability/`.
- Azure IaC scaffold lives under `azure/iac/`.

## Components

### Observability

- `docker/compose.observability.yaml`
  - Adds optional profile for OTel collector, Prometheus, Grafana
- `docker/observability/otel-collector-config.yaml`
  - OTLP receiver, batch + memory processors, Prometheus exporter
- Grafana provisioning and starter dashboards

### Azure deployment

- `azure/iac/appservice-acr.bicep`
  - ACR + Linux App Service + system-assigned identity + AcrPull role assignment
- `azure/iac/appservice-acr.parameters.json`
  - baseline parameters for non-prod bootstrap
- `.github/workflows/deploy-appservice-acr.yml`
  - manual OIDC-based build/push/deploy workflow scaffold

### Documentation and developer ergonomics

- `README.md`, `docker/README.md`, `azure/README.md`, `.env.example`
- `.vscode/settings.json` YAML schemas for Grafana provisioning files
- `.vscode/extensions.json` recommendations for Storybook/Codecov/Azure App Service

## Rollback strategy

- Remove `compose.observability.yaml` and `docker/observability/`
- Revert compose/docs/env changes
- Remove Azure IaC scaffold and deployment workflow

No data migrations or runtime schema migrations are part of this change.
