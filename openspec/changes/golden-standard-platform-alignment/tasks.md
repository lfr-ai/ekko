# Tasks: Golden standard platform alignment

## Completed foundation

- [x] Audit current repo against the golden baseline
- [x] Add dedicated observability compose file
- [x] Add OTel collector + Prometheus + Grafana provisioning configs
- [x] Update Docker docs and env template
- [x] Add Azure App Service + ACR Bicep scaffold
- [x] Add manual CI workflow scaffold for Azure deploy path
- [x] Update VS Code settings/extensions for observability + frontend workflow
- [x] Remove deprecated observability config duplication
- [x] Add comprehensive audit report with phased TODOs for:
   - LiteLLM + LangChain migration
   - SQLite local migration strategy
   - OTel/Prometheus/Grafana production path

## Phase 0 — quality gate stabilization

- [x] Harden duplicate scan scope to exclude non-source runtime/vendor trees causing OOM failures.
- [x] Validate `task lint:duplicates` completes successfully and still catches first-party clone regressions.
- [x] Validate `task check` and `task verify` locally with deterministic pass/fail behavior.

## Phase 1 — dependency modernization

- [x] Upgrade FastAPI to target stable version and reconcile any router/runtime compatibility changes.
- [x] Upgrade Strawberry GraphQL to target stable version and apply any required migration adjustments.
- [x] Re-run full backend/frontend lint, typecheck, and test suites after upgrades.
- [x] Re-run GraphQL schema contract checks and refresh baseline only when intentional.

## Phase 2 — GraphQL demand-control hardening

- [x] Design and implement persisted/trusted operation strategy for first-party clients.
- [x] Introduce complexity/cost control policy for GraphQL operations.
- [x] Add tests for depth/alias/token/cost budget rejection behavior.

## Phase 3 — subscription/auth hardening

- [x] Add explicit subscription connect authorization policy.
- [x] Add integration tests for authorized and unauthorized subscription connection flows.
- [x] Verify no authorization business logic leaks into infrastructure-agnostic layers.

## Phase 4 — error contract unification

- [x] Standardize expected domain errors as typed GraphQL results (errors-as-data).
- [x] Keep exceptional/system failures in top-level GraphQL errors with production-safe masking.
- [x] Add tests for contract-level error behavior across queries/mutations/subscriptions.

## Phase 5 — GraphQL-first completion

- [x] Define and document deprecation window for residual REST stream surface.
- [x] Implement compatibility-safe removal path and migration notes for clients.
- [x] Validate no contract regressions for GraphQL-first clients.

## Phase 6 — PII policy hardening

- [x] Introduce policy-profile-driven PII behavior where applicable.
- [x] Add coverage for all user-content ingress paths requiring anonymization.
- [x] Add tests for edge cases and false-positive/false-negative minimization.

## Phase 7 — observability and readiness verification

- [x] Add GraphQL operation metrics and traces for performance and security analysis.
- [x] Add alerting/dashboards for anomalous query behavior.
- [x] Validate observability compose profile startup and telemetry pipeline health.

## Final acceptance gate

- [x] Run full local quality gate and readiness checks:
   - `task lint`
   - `task typecheck`
   - `task test`
   - `task check`
   - `task verify`
- [x] Confirm docs/config/env files fully align with implemented behavior.
- [x] Confirm forbidden external-reference token scan passes.
