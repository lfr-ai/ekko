# Proposal: Golden standard platform alignment

## Why

The repository already has strong foundations, but requires additional alignment for:

- portable/project-agnostic agentic setup quality
- dedicated observability stack with OTel collector + provisioning
- Azure App Service + ACR deployment scaffolding
- explicit implementation roadmap for LiteLLM + LangChain migration

## What changes

1. Docker observability split and hardening
2. Azure App Service + ACR IaC template and workflow scaffold
3. Developer tooling and docs synchronization updates
4. Full audit + TODO roadmap artifacts for LiteLLM, database strategy, and observability

## Non-goals

- full LiteLLM migration in this change
- full OpenTelemetry instrumentation in application code
- production secret wiring in CI

## Risk boundaries

- no behavioral business-logic changes
- no API contract changes
- changes are additive/configuration-focused

## Success criteria

- Local observability stack starts with dedicated compose profile
- Azure IaC scaffold validates and documents required inputs
- Docs and env templates reflect new setup
- Audit artifact contains explicit phased TODOs
