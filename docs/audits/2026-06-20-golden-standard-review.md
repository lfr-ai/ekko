# Golden Standard Review — 2026-06-20

## Scope

This review compares `ekko` against the reference baseline in:

- `C:\Users\LFR\OneDrive - AP Pension\Documents\projects\koda_automation`
- `C:\Users\LFR\OneDrive - AP Pension\Documents\projects\kris_frontend`
- `C:\Users\LFR\OneDrive - AP Pension\Documents\projects\claim_handler_v3`
- `C:\Users\LFR\OneDrive - AP Pension\Documents\projects\copier-fullstack-template`

It focuses on:

- Agentic setup (Copilot/agents/skills/MCP/OpenSpec/GitNexus)
- Frontend readiness (Storybook/Playwright/shadcn/favicon)
- Docker/Caddy/Azure production-readiness scaffolding
- CI quality/security/deployment coverage
- Data platform roadmap (SQLite local, PostgreSQL dev/prod)
- AI platform roadmap (LiteLLM + LangChain abstraction)
- Observability roadmap (Prometheus + Grafana + OTel collector)
- Optional analytics roadmap (Matomo local profile)

## Executive summary

`ekko` is already mature and, in several areas, exceeds the current `koda_automation` baseline:

- richer agent catalog and frontend-specialist agents
- Storybook + Playwright + shadcn MCP already wired
- OpenSpec artifacts and schema usage already standardized
- SQLite local + PostgreSQL dev/prod strategy already implemented in settings

This change set strengthens remaining gaps:

1. split observability into dedicated compose stack (`compose.observability.yaml`)
2. add OTel collector baseline and Grafana provisioning
3. add Azure App Service + ACR IaC scaffold and CI deploy workflow scaffold
4. tighten developer extension recommendations and observability schema support
5. clean up duplicate ignore entries and keep docs in sync
6. add optional Matomo analytics profile and task wrappers

## Key findings by area

### 1) Agentic setup

Status: **Strong**

- `.github/agents/` includes frontend, UI/UX, Storybook, Playwright, shadcn, testing, security, devops.
- `.github/skills/` includes OpenSpec + frontend + quality + gitnexus + shadcn + accessibility skills.
- `.vscode/mcp.json` and `.mcp.json` already include:
  - `context7`
  - `gitnexus`
  - `playwright`
  - `shadcn`
  - `storybook`

Action taken:

- minor project-agnostic wording cleanup in `.coderabbit.yaml`.

### 2) Frontend + UI tooling

Status: **Strong**

- Storybook configured (`frontend/.storybook/*`)
- Story tests + a11y checks configured
- favicon already present (`frontend/public/favicon.svg`) and referenced by `frontend/index.html`

Action taken:

- extension recommendations strengthened with `storybookjs.storybook-vscode`, `codecov.codecov`, and Azure App Service extension.

### 3) Docker / Caddy / Observability

Status before: **Partially mature** (observability mixed into base compose, no OTel collector, no Grafana provisioning)

Action taken:

- base compose now minimal (`app`, optional `caddy`)
- observability moved to `docker/compose.observability.yaml`
- added OTel collector (`otel/opentelemetry-collector-contrib`)
- added Prometheus config under `docker/observability/prometheus.yml`
- added Grafana provisioning + starter dashboard
- updated docs and env template

### 3b) Optional analytics profile (Matomo)

Status: **Added**

Action taken:

- added `docker/compose.analytics.yaml` for optional Matomo + MariaDB profile
- added task wrappers (`task docker:up:analytics`, `task docker:up:full`)
- updated `.env.example`, `README.md`, and `docker/README.md`

### 4) Azure IaC + deployment

Status before: **Minimal**

Action taken:

- added `azure/iac/appservice-acr.bicep` (ACR + Linux App Service + managed identity + AcrPull)
- added `azure/iac/appservice-acr.parameters.json`
- updated `azure/README.md` deployment instructions
- added workflow scaffold: `.github/workflows/deploy-appservice-acr.yml`

### 5) CI / Quality / Security

Status: **Strong baseline**

- CI covers lint/type/test/security/architecture/openspec/playwright/storybook
- codecov workflow exists
- codeql/security workflows exist

Action taken:

- no breaking CI rewires in this patch; deployment workflow added as opt-in/manual.

## Deep-dive: execution flow / handlers / pipeline

Observed high-level flow:

1. app bootstrap in `backend/src/ekko/composition/app_factory.py#create_app`
2. settings + container + middleware registration
3. REST + GraphQL routes mounted
4. application services (`chat_service`, `summarizer_service`) orchestrate through ports
5. AI orchestration under `backend/src/ekko/ai/crewai/`

Current architecture direction remains clean:

- presentation delegates to application
- infrastructure implements ports
- core stays framework-light

## Deep-dive: database / SQL setup

Current strategy in code is already aligned with requested target:

- local/test default to SQLite
- dev/prod default to PostgreSQL
- migration utility exists: `backend/src/ekko/cli/postgres_to_sqlite.py`
- docs already mention `task db:migrate:pg-to-sqlite`

## Deep-dive: observability

New local baseline now supports:

- OpenTelemetry collector receiver (`4317`/`4318`)
- Prometheus scraping app + collector metrics
- Grafana auto-provisioned datasource + dashboard

## Extensive implementation TODO — LiteLLM + LangChain

### Phase 0 — design and safety gates

- [ ] Create OpenSpec change dedicated to LLM gateway modernization.
- [ ] Define non-goals (no provider lock-in, no hardcoded vendor params).
- [ ] Add contract tests around existing `ChatPort` behavior before migration.

### Phase 1 — abstraction layer

- [ ] Introduce provider-agnostic `LLMGatewayPort` in `core/ports/`.
- [ ] Define request/response value objects with strict typing.
- [ ] Add error taxonomy mapping (auth, rate-limit, timeout, policy, unknown).

### Phase 2 — LiteLLM adapter

- [ ] Add `litellm` dependency and adapter in infrastructure.
- [ ] Implement `Router` config with fallback + retry + cooldown + weighted routing.
- [ ] Add per-model routing groups for latency-sensitive vs batch use cases.
- [ ] Add Redis-backed cache support for production and in-memory for local.

### Phase 3 — LangChain integration

- [ ] Introduce LangChain model wrapper pointed at LiteLLM (OpenAI-compatible format).
- [ ] Route existing chain/tool calls through unified gateway.
- [ ] Add tracing hooks for LangSmith/OTel callbacks.

### Phase 4 — governance and reliability

- [ ] Add cost tracking callbacks and request metadata logging.
- [ ] Add policy guards (max tokens, model allowlist, timeout budgets).
- [ ] Add burn-rate and rejection-rate metrics.

### Phase 5 — rollout

- [ ] Feature-flag migration path (`EKKO_LLM_BACKEND=legacy|litellm`).
- [ ] Dual-run shadow mode for response parity checks.
- [ ] Cut over per endpoint after SLO + quality thresholds pass.

## Extensive implementation TODO — SQLite local migration strategy

### Phase 0 — verification

- [ ] Inventory all database connection sources (settings, alembic, scripts, tests).
- [ ] Verify all local developer paths default to SQLite.

### Phase 1 — migration execution

- [ ] Back up local PostgreSQL DB.
- [ ] Run `task db:migrate:pg-to-sqlite` and verify row counts by table.
- [ ] Validate referential integrity and key constraints in SQLite.

### Phase 2 — developer UX hardening

- [ ] Remove local PostgreSQL from default compose/dev tasks.
- [ ] Keep explicit optional profile for PostgreSQL integration testing only.
- [ ] Add data consistency checker script (`row_count`, `hash`, `null-rate`).

### Phase 3 — docs and CI

- [ ] Update onboarding docs with SQLite-first local setup.
- [ ] Ensure integration tests requiring PostgreSQL clearly marked and isolated.

## Extensive implementation TODO — observability (Prometheus/Grafana/OTel)

### Phase 0 — baseline

- [x] Add local observability compose file.
- [x] Add OTel collector config.
- [x] Add Grafana provisioning and starter dashboard.

### Phase 1 — app instrumentation

- [ ] Add OpenTelemetry Python SDK + FastAPI/HTTPX/SQLAlchemy instrumentation.
- [ ] Emit traces, metrics, and structured logs with correlation IDs.
- [ ] Add custom metrics for:
  - [ ] AI approval rate
  - [ ] orchestrator run count/duration
  - [ ] model/provider error rates
  - [ ] token usage and latency by route

### Phase 2 — production exporters

- [ ] Configure OTLP export to Azure Monitor / managed backend.
- [ ] Add retry/batch/resource attributes in collector pipelines.
- [ ] Add PII scrubbing policy in telemetry processors.

### Phase 3 — dashboards + alerts

- [ ] Create SLO dashboards (latency, errors, saturation).
- [ ] Add alerts for approval-rate regressions and orchestration failures.
- [ ] Add runbook links to alert descriptions.

## Extensive implementation TODO — Matomo analytics

### Phase 0 — local baseline

- [x] Add optional compose profile with isolated data volumes.
- [x] Add env-template variables for local development.
- [x] Add task wrappers and docker docs.

### Phase 1 — frontend integration

- [ ] Add a typed analytics adapter in frontend infrastructure.
- [ ] Gate telemetry by explicit user consent configuration.
- [ ] Disable tracking in test runs and Storybook by default.

### Phase 2 — backend correlation

- [ ] Propagate request/session correlation IDs to frontend responses.
- [ ] Add optional event forwarding contract for key backend events.
- [ ] Validate no PII leakage in analytics payloads.

## Open risks

- Deployment workflow requires repository secrets and federated identity setup.
- Grafana starter dashboard assumes common metric names; adapt to actual exported metric names once app instrumentation is enabled.
- LiteLLM rollout should be feature-flagged to avoid regressions in existing prompt/agent pipelines.

## Recommended immediate next steps

1. Enable and test observability profile locally.
2. Validate Azure IaC deployment in non-prod resource group.
3. Open a dedicated OpenSpec change for LiteLLM migration and execute in TDD slices.
4. Add instrumentation PR focused only on metrics/traces (no business logic changes).
