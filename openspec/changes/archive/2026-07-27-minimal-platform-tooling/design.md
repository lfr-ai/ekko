# Design: Minimal platform tooling baseline

## Design intent

Close all concrete gaps identified by exhaustive structural review while
preserving existing architecture decisions that are
intentionally different (monorepo layout, frontend tooling, GraphQL layer).

## Principles

1. Prefer fewer moving parts.
2. Prefer explicit defaults over implicit behavior.
3. Keep security and architecture checks high-signal.
4. Avoid duplicate policy definitions across files.
5. Keep runtime setup optional unless required.
6. Only rename/restructure when the benefit clearly exceeds the churn cost.

## Boundary impact

- No domain/application/infrastructure code behavior changes.
- Changes target config, tooling, documentation, and spec artifacts only.

## Structural decisions

### Intentional project decisions (keep as-is)

| Area | Alternative | Ekko | Reason to keep |
|------|-----------|------|----------------|
| Package name | `configs/` (plural) | `config/` (singular) | internally consistent |
| Prompt location | top-level `prompts/` | `ai/prompts/` | domain-appropriate nesting |
| Frontend tooling | none | full React/Vite stack | full-stack monorepo |
| MCP servers | 2 (context7, gitnexus) | 5 (+shadcn, playwright, storybook) | frontend-relevant |
| Agent count | 9 | 17 | broader full-stack scope |
| Root pyproject | present | at `backend/` | monorepo layout |

### Gaps to close (implement)

| Gap | Current state | Target state |
|-----|---------------|--------------|
| diff-cover | absent | in tox coverage env + dev deps |
| `.cz.toml` version_files | missing | `["backend/src/ekko/__init__.py:__version__"]` |
| AGENTS.md depth | 7 rules | expanded to the approved policy set |
| Pre-commit ty hook naming | `ty-check` | `ty` |
| Prompt registry experimental | implemented but architecture differs | confirm experimental-mode works correctly |
| IaC subscription-scope entry | missing | `azure/iac/deploy.bicep` |
| IaC modular Bicep | monolithic files | `azure/iac/modules/` with factored resources |
| IaC environment parameters | flat JSON | `azure/iac/parameters/{dev,prod}/*.bicepparam` |
| IaC deploy script | missing | `azure/scripts/deploy.azcli` |
| Compiled ARM JSON in source | legacy compiled ARM JSON tracked | remove; build from `.bicep` |
| Docker port binding | `8000:8000` (all interfaces) | `127.0.0.1:8000:8000` |
| LLM chat adapter | LangChain `init_chat_model()` | LiteLLM `completion()` / `acompletion()` |
| LLM dependency scope | LangChain for everything | LiteLLM for chat; LangChain only for chains/RAG |
| README style | emoji-heavy, verbose | minimal professional, no emojis |
| Docstring delimiters | already `"""` | confirm `"""` (triple-double-quote) Google convention throughout |
| Docstring typing | inconsistent | typed Args/Returns/Raises in all multi-line |

### Conventions confirmed OK (no changes needed)

| Area | Status | Notes |
|------|--------|-------|
| Config factory | OK | `get_settings()` naming is project-appropriate |
| Logging | OK | Stdlib logging with structured JSON formatter |
| App factory location | OK | `composition/app_factory.py` (monorepo layout) |
| GraphQL layer | OK | Ekko-only feature, well-structured |
| Extra middleware | OK | auth/CORS/request-id/security-headers/timing are project-appropriate |
| WebSocket support | OK | Project-appropriate for real-time voice platform |
| Dependency update tooling | OK | `renovate.json` present in both repos |
| LangChain for chains/RAG | OK | Keep for `ai/chains/` and `ai/crewai/`; remove from chat path |
| ChatPort protocol | OK | Core port unchanged; only infrastructure adapter swaps |

## Components covered

- Coverage gating (`tox.ini`, `backend/pyproject.toml`)
- Commitizen config (`.cz.toml`)
- Agent policy (`AGENTS.md`)
- Pre-commit hooks (`.pre-commit-config.yaml`)
- Codecov policy (`codecov.yml`)
- CodeRabbit policy (`.coderabbit.yaml`)
- Keploy task contracts (`Taskfile.yml`, `tasks/backend.yml`)
- Observability profile contract (`docker/compose.observability.yaml`)
- Environment template policy (`.env.example`)
- Agentic/MCP parity (`.mcp.json`, `.vscode/mcp.json`)
- GitNexus readiness precondition
- Documentation style

## Rollout model

Phase 1: Spec definition (this change -- explore output)
Phase 2: Config/tooling implementation (`/opsx-apply`)
Phase 3: Validation and simplification pass
