# Design: Golden standard platform alignment

## Architecture impact

This change is infrastructure/configuration-centric and preserves existing Clean Architecture dependencies.

- Application and domain code are not re-layered.
- New observability files live under `docker/observability/`.
- Azure IaC scaffold lives under `azure/iac/`.

Additional design constraints for implementation phases:

- GraphQL transport remains a thin presentation adapter.
- Authorization decisions remain delegated to application/business boundaries.
- PII handling remains centralized and reusable (no scattered ad-hoc redaction).
- Dependency upgrades must be behavior-preserving and test-gated.

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

### GraphQL platform hardening

- `backend/src/ekko/presentation/graphql/schema.py`
  - Keep depth/alias/token limits and batching constraints as baseline controls.
  - Introduce cost-complexity policy extension points and operation governance.
- `backend/src/ekko/presentation/graphql/router.py`
  - Maintain masked production error shaping.
  - Add explicit subscription connect authorization policy.
  - Preserve context injection boundaries via composition/app state.
- GraphQL contract governance artifacts
  - Keep schema contract checks authoritative and updated intentionally.

### Quality gate reliability

- `jscpd.json`
  - Exclude non-source runtime/vendor trees that create OOM risk.
  - Preserve strict duplicate detection for first-party code.
- Root quality tasks
  - Ensure local and CI quality paths are deterministic and reproducible.

### Documentation and developer ergonomics

- `README.md`, `docker/README.md`, `azure/README.md`, `.env.example`
- `.vscode/settings.json` YAML schemas for Grafana provisioning files
- `.vscode/extensions.json` recommendations for Storybook/Codecov/Azure App Service

### Phase validation matrix

- Phase 0: `task lint:duplicates`, `task check`, `task verify`
- Phase 1: backend + frontend lint/type/tests and GraphQL contract check
- Phase 2-4: GraphQL unit/integration tests + schema contract check + security-oriented scenario tests
- Phase 5: migration compatibility tests (GraphQL + deprecated REST transition checks)
- Phase 6: PII unit/property/integration coverage checks
- Phase 7: observability stack startup + telemetry sanity assertions

All phases require docs/config sync updates when behavior or setup changes.

## Rollback strategy

- Remove `compose.observability.yaml` and `docker/observability/`
- Revert compose/docs/env changes
- Remove Azure IaC scaffold and deployment workflow

For phased hardening work:

- Revert one phase at a time to preserve bisectability.
- Keep compatibility toggles during deprecation windows.
- Never combine dependency major upgrades with endpoint removals in the same rollback unit.

No data migrations or runtime schema migrations are part of this change.
