# Proposal: Golden standard platform alignment

## Why

The repository already has strong foundations, but requires additional alignment for:

- portable/project-agnostic agentic setup quality
- dedicated observability stack with OTel collector + provisioning
- Azure App Service + ACR deployment scaffolding
- explicit implementation roadmap for LiteLLM + LangChain migration
- production-grade GraphQL security and governance hardening
- complete deprecation path from residual REST surface to GraphQL-first contracts
- reliability hardening for local and CI quality gates

## What changes

1. Docker observability split and hardening
2. Azure App Service + ACR IaC template and workflow scaffold
3. Developer tooling and docs synchronization updates
4. Full audit + TODO roadmap artifacts for LiteLLM, database strategy, and observability
5. GraphQL production hardening roadmap (authz/authn boundaries, demand control, error contract policy)
6. Repository quality gate stabilization roadmap (duplicate scan reliability, deterministic checks)
7. Phased migration roadmap to complete GraphQL-first platform posture

## Phase-based implementation roadmap

### Phase 0 — quality gate stabilization

- Stabilize `task lint:duplicates` by excluding non-source vendored/runtime trees that currently cause memory blowups.
- Ensure duplicate detection remains strict for first-party code while avoiding generated/third-party directories.
- Validate `task check` and `task verify` complete deterministically on developer machines and CI.

### Phase 1 — dependency and runtime modernization

- Upgrade FastAPI and Strawberry in a controlled, test-gated sequence.
- Reconcile any framework-level router/typing/runtime changes.
- Preserve API behavior, schema compatibility, and existing test guarantees.

### Phase 2 — GraphQL demand-control hardening

- Add persisted/trusted operations strategy for first-party clients.
- Add operation cost/complexity policy and enforcement.
- Add explicit limits and metrics for expensive operations.

### Phase 3 — GraphQL subscription/auth hardening

- Add explicit WebSocket/SSE subscription handshake authorization policy.
- Ensure auth decisions stay in the business logic/application boundary (no auth logic leakage into transport plumbing).
- Add tests for accept/reject/timeout/reconnect security scenarios.

### Phase 4 — error contract unification

- Standardize exceptional errors as top-level GraphQL errors.
- Standardize expected domain validation outcomes as typed schema results (errors-as-data patterns).
- Keep internal details masked in production while preserving debuggability in local/test.

### Phase 5 — complete GraphQL-first transition

- Finalize deprecation/removal path for residual REST stream endpoints.
- Maintain backward-compatible migration window with explicit sunset milestones.
- Keep schema contract snapshots stable across transitional releases.

### Phase 6 — PII and governance hardening

- Confirm all user-provided content ingress points are covered by PII policy where required.
- Add policy-profile-driven PII behavior (strict/standard) with deterministic tests.
- Add audit-level observability for redaction outcomes without exposing sensitive payloads.

### Phase 7 — observability and production readiness verification

- Expand GraphQL metrics and traces (operation class, failure mode, budget/cost signals).
- Add alerting and dashboard baselines for anomalous query behavior.
- Run end-to-end readiness checks and document operational runbooks.

## Non-goals

- full LiteLLM migration in this change
- full OpenTelemetry instrumentation in application code
- production secret wiring in CI
- broad business-domain redesign unrelated to platform hardening

## Risk boundaries

- no silent behavioral business-logic drift
- no uncontrolled API/GraphQL contract breakage
- all risky migrations must be phased behind explicit validation gates

## Success criteria

- Local observability stack starts with dedicated compose profile
- Azure IaC scaffold validates and documents required inputs
- Docs and env templates reflect new setup
- Audit artifact contains explicit phased TODOs
- Duplicate detection is reliable and no longer fails due to vendored/generated trees
- GraphQL production hardening controls are documented, implemented, and verified
- Quality gate passes remain green after modernization and hardening phases
