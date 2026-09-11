# Tasks: Minimal platform tooling baseline

## Phase 1 — spec definition (explore output)

- [x] Exhaustive structural platform review.
- [x] Add requirement deltas for minimal Codecov policy.
- [x] Add requirement deltas for minimal CodeRabbit policy.
- [x] Add requirement deltas for Keploy task contracts.
- [x] Add requirement deltas for minimal Prometheus/Grafana profile behavior.
- [x] Add requirement deltas for `.env.example` inclusion/exclusion policy.
- [x] Add requirement deltas for agentic/MCP parity.
- [x] Add requirement deltas for GitNexus index-readiness precondition.
- [x] Add requirement for diff-cover gate in tox coverage environment.
- [x] Add requirement for `.cz.toml` version_files.
- [x] Add requirement for prompt registry version-set architecture.
- [x] Add requirement for comprehensive AGENTS.md hard rules.
- [x] Add requirement for pre-commit hook naming consistency.
- [x] Add requirement for Clean Architecture boundary enforcement.
- [x] Document intentional structural decisions in design.md.
- [x] Add requirements for IaC subscription-scope entry + modular Bicep.
- [x] Add requirements for environment-split `.bicepparam` parameters.
- [x] Add requirement for deploy script.
- [x] Add requirement to remove compiled ARM JSON from source control.
- [x] Add requirement for Docker loopback port bindings.
- [x] Add requirement for ACR-deployable container image.
- [x] Add requirement for LiteLLM-based provider-agnostic LLM adapter.
- [x] Add requirement for LLM retry/fallback across deployments.
- [x] Add requirement for LLM observability callbacks.

## Phase 2 — implementation (next `/opsx-apply`)

### Critical gaps

- [x] Add `diff-cover` to backend dev dependencies in `backend/pyproject.toml`.
- [x] Add `diff-cover` command to `tox.ini` coverage environment.
- [x] Add `version_files` to `.cz.toml`.
- [x] Expand AGENTS.md hard rules to the approved policy depth.
- [x] Rename pre-commit `ty-check` hook to `ty` for consistency.

### IaC alignment

- [x] Create `azure/iac/deploy.bicep` (subscription-scope entry point).
- [x] Refactor `azure/iac/main.bicep` to compose modules from `azure/iac/modules/`.
- [x] Create `azure/iac/modules/` with factored resource modules.
- [x] Create `azure/iac/parameters/dev/deploy.dev.bicepparam`.
- [x] Create `azure/iac/parameters/prod/deploy.prod.bicepparam`.
- [x] Create `azure/scripts/deploy.azcli` deploy script.
- [x] Remove legacy compiled ARM JSON artifacts.
- [x] Remove `azure/iac/main.parameters.json` (replaced by `.bicepparam`).
- [x] Remove legacy flat JSON parameter files (replaced by `.bicepparam`).

### Docker alignment

- [x] Bind `compose.override.yaml` ports to `127.0.0.1:` loopback.

### Documentation and conventions alignment

- [x] Rewrite `README.md` to minimal professional style (no emojis, single-screen quickstart).
- [x] Confirm all docstrings use `"""` (triple-double-quote) with Google-style conventions (imperative mood for functions, noun phrase for classes).
- [x] Ensure all multi-line docstrings include typed Args/Returns/Raises sections.
- [x] Confirm `dependency_registry.py` follows canonical DI pattern.
- [x] Confirm `responses.py` error constants follow canonical structure.
- [x] Confirm `exception_handlers.py` masks domain internals in production.
- [x] Confirm GraphQL schema has demand-control extensions configured.
- [x] Confirm WebSocket/subscription authorization is enforced.
- [x] Confirm `renovate.json` targets all ecosystems (Python, JS, Docker, Actions).

### LiteLLM migration

- [x] Add `litellm` to backend dependencies in `backend/pyproject.toml`.
- [x] Create `infrastructure/llm/litellm_adapter.py` implementing `ChatPort` via LiteLLM.
- [x] Update `composition/container.py` to wire LiteLLM adapter as default `ChatPort`.
- [x] Configure LiteLLM model name prefix convention in settings (`openai/`, `azure/`).
- [x] Add retry/fallback configuration via LiteLLM Router or settings.
- [x] Add optional observability callback configuration (Langfuse, OTel).
- [x] Remove direct `langchain.chat_models.init_chat_model` usage from chat adapter.
- [x] Keep LangChain dependency only for `ai/chains/` and `ai/crewai/` if needed.
- [x] Add unit tests for LiteLLM adapter (sync + async + error mapping).

### Simplification and cleanup

- [x] Simplify `codecov.yml` to minimal required controls only.
- [x] Simplify `.coderabbit.yaml` to high-signal architecture/security review only.
- [x] Remove duplicate OpenSpec prompt structures (consolidate `opsx-*.prompt.md` flat files with `openspec/` subfolder or vice versa).
- [x] Ensure `.env.example` entries follow required/optional/secret policy.
- [x] Ensure documentation is minimal, professional, and emoji-free throughout.

### Validation and parity

- [x] Confirm Keploy task wrappers are documentation-consistent.
- [x] Confirm observability profile remains optional and minimal.
- [x] Confirm MCP parity between `.mcp.json` and `.vscode/mcp.json`.
- [x] Confirm prompt registry experimental-mode functions correctly.
- [x] Confirm architecture boundary checker runs without violations.
- [x] Confirm no references to external repository paths exist in codebase.

## Phase 3 — verification

- [x] Run full quality gate (`task check`).
- [x] Validate OpenSpec artifacts (`openspec validate --all --strict`).
- [x] Validate Bicep templates compile (`az bicep build`).
- [x] Confirm no architecture-boundary regressions.
- [x] Confirm diff-cover gate works in tox coverage environment.
