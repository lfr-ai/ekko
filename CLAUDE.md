# CLAUDE.md

@AGENTS.md

This file is the **primary instruction set** for Claude Code CLI (`claude`) when
operating inside the `ekko` repository. It is read automatically on every
invocation and takes precedence over general model knowledge.

> **Instruction precedence** (highest to lowest):
>
> 1. This file (`CLAUDE.md`)
> 2. Path-scoped rules (`.claude/rules/*.md`)
> 3. Skill packs (`.github/skills/*/SKILL.md`)
> 4. Copilot instructions (`.github/copilot-instructions.md`)
> 5. `AGENTS.md` (generic agent guidance, imported above)
> 6. General model knowledge

---

## Default Working Method

Apply this to every task unless the user explicitly asks for a lighter touch:

**IMPORTANT!** You MUST be exhaustive and follow best practices. Consult, search,
and fetch the web and relevant documentation. Make an extensive TODO/plan, then
run a systematic walkthrough ensuring everything is addressed and considered —
clean, aligned, consistent, up to date, and working. Keep cognitive load
manageable and follow the existing structure, setup, and conventions. Enforce
Clean Architecture and ensure alignment and consistency throughout the codebase.

## Response Format

End every response with a short `tldr;` section, placed **last** so it is easy to
find. Keep it minimal and human-readable — only the most important information
(key files touched, changes made, and any next step) as a few tight bullets, with
no extra prose. Omit the `tldr;` only when the user explicitly requests otherwise.

---

## 1. Project Overview

**Ekko** is an AI-powered voice assistant platform that captures desktop audio,
transcribes speech, runs AI pipelines (summarization, PII scrubbing), and
presents results through a local web UI.

| Attribute | Value |
| --- | --- |
| Runtime | Python 3.14, FastAPI, Uvicorn |
| ORM | SQLAlchemy 2.0+ async, SQLite via aiosqlite |
| AI | LiteLLM, OpenAI, Azure Speech |
| GraphQL | Strawberry GraphQL (single read-only query) |
| Frontend | React 19, TypeScript, Vite 6 + SWC, shadcn/ui, Tailwind CSS v4 |
| State | Zustand, TanStack React Query |
| Backend pkg mgr | `uv` |
| Frontend pkg mgr | `bun` |
| Task runner | Taskfile.yml (root + `tasks/`) |
| Architecture | Clean Architecture, strict layered boundaries |
| Auth | Auto-authenticates as `dev-user` (no JWT, local-only) |
| Deployment | Local desktop EXE via PyInstaller |

---

## 2. Quick Commands

```bash
# Development
task dev                  # Start backend + frontend
task dev:backend          # Backend only
task dev:frontend         # Frontend only

# Testing
task test                 # Default tests (backend unit + frontend unit)
task test:unit            # Unit tests only
task test:integration     # Integration tests
task test:property        # Hypothesis property-based tests
task test:performance     # Benchmark tests
task test:e2e             # End-to-end tests
task test:frontend        # Frontend unit tests (Vitest)
task test:coverage        # Tests with coverage reports

# Quality
task lint                 # Run all linters
task format               # Format all code
task typecheck            # Type check (ty + frontend tsc)
task xenon                # Cyclomatic complexity gate
task check                # Full quality gate (lint + test:unit + typecheck + xenon)
task pre-commit           # Run pre-commit on all files

# Database
task db:migrate           # Run Alembic migrations
task db:revision          # Create new Alembic migration
task db:downgrade         # Rollback last migration
task db:reset             # Delete SQLite DB and re-migrate

# Build & Deploy
task build:exe            # Build standalone PyInstaller EXE
task docker:up:caddy      # Start Docker stack with Caddy

# Registry
task registry:generate    # Regenerate constants from naming_registry.json

# Validation (run before finalizing any change)
task test && task lint && task typecheck && task pre-commit
```

---

## 3. Source Layout

### Backend

```text
backend/src/ekko/
├── core/                # Domain entities, value objects, ports, exceptions
│   ├── entities/        # Domain entities
│   ├── value_objects/   # Immutable value objects
│   ├── ports/           # Port protocols (audio, chat, pii, prompts, repositories)
│   ├── exceptions/      # Domain exception hierarchy
│   ├── enums/           # Domain enumerations (base, ai, audio, messaging)
│   ├── events.py        # Domain events
│   ├── types.py         # Domain type aliases
│   └── registry_constants.py  # Generated naming constants
├── application/         # DTOs, handlers, services, mappers
│   ├── dtos/            # Data transfer objects
│   ├── handlers/        # Application handlers
│   ├── mappers/         # Entity <-> DTO mappers
│   └── services/        # Orchestration services (summarizer)
├── infrastructure/      # Persistence (ORM), clients, adapters
│   ├── adapters/        # Audio, STT adapters
│   ├── audio_streamer/  # Audio streamer TCP server
│   ├── clients/         # External service clients (chat, prompt registry)
│   ├── concurrency/     # QueueManager, ThreadManager
│   ├── db/              # SQLAlchemy engine, models (SQLite via aiosqlite)
│   ├── helpers/         # Retry policies
│   └── stt/             # Speech-to-text transcriber
├── ai/                  # AI vertical
│   ├── chains/          # Conversational chains
│   ├── pii/             # PII anonymization (regex-based)
│   └── prompts/         # Prompt registry, templates, and versioning
├── presentation/        # FastAPI routes, GraphQL, middleware, DI
│   ├── api/             # REST routes, dependencies, middleware
│   └── graphql/         # Strawberry schema, single read-only query
├── composition/         # DI container + app factory
├── config/              # Faceted settings + environment configs
│   ├── settings/        # ConfiguredSettings base + per-domain facets (*Settings)
│   ├── environments/    # Per-environment configs (local/dev/prod/test_env)
│   ├── base.py          # BaseAppConfig (composes all settings facets)
│   └── runtime.py       # Environment resolution + get_config() factory
└── cli/                 # CLI entry points
```

### Frontend

```text
frontend/src/
├── application/         # Hooks and state management (Zustand stores)
├── domain/              # Models, types, schemas (Zod)
├── infrastructure/      # API clients, config
├── lib/                 # Utilities (cn helper)
├── presentation/        # Components (ui/common/layout), pages, features, styles
└── router/              # React Router config
```

### Tests

```text
tests/
├── unit/                # Fast, isolated, no I/O
├── integration/         # Database, API boundary tests
├── property/            # Hypothesis property-based tests
├── performance/         # Benchmark and timing tests
├── e2e/                 # End-to-end tests
├── database/            # Migration and ORM model tests
├── factories/           # factory-boy factories
├── fixtures/            # Shared test data
├── mocks/               # Reusable mock objects
└── utils/               # Assertion helpers
```

### Support Directories

```text
tasks/                   # Split Taskfile includes (backend.yml, frontend.yml)
tools/                   # Convention checkers and security audits
registry/                # Naming registry (JSON -> generated constants)
```

---

## 4. Architecture Rules

### Dependency Direction

```text
config -> core -> {ai | infrastructure} -> application -> presentation -> composition -> cli
```

Dependencies always point **inward**. Outer layers depend on inner layers, never
the reverse. The `core/` layer has zero framework imports. Enforced by
import-linter contracts in `backend/.importlinter` (`task architecture`).

### Import Rules

| Layer | May Import From | NEVER Imports From |
| --- | --- | --- |
| `config/` | external libs, stdlib | `core/`, `infrastructure/`, `ai/`, `application/`, `presentation/` |
| `core/` | `config/`, stdlib (+ Pydantic hooks) | `infrastructure/`, `ai/`, `application/`, `presentation/` |
| `infrastructure/` | `core/`, `config/`, external libs | `ai/`, `application/`, `presentation/` |
| `ai/` | `core/`, `config/` | `infrastructure/`, `application/`, `presentation/` |
| `application/` | `core/`, `infrastructure/`, `ai/`, `config/` | `presentation/` |
| `presentation/` | `application/`, `core/`, `config/` | `infrastructure/`, `ai/`, `composition/` |
| `composition/` | all layers (DI wiring) | — |
| `cli/` | `composition/`, `presentation/`, `config/` | (entrypoint) |

### DI Pattern

- `composition/Container` wires all dependencies using `@cached_property`.
- `presentation/api/dependencies.py` exposes FastAPI `Depends()` callables.
- Concrete classes implement protocols declared in `core/ports/`.

---

## 5. Hard Rules

These are non-negotiable. Every change must satisfy all of them.

| # | Rule | Details |
| --- | --- | --- |
| 1 | **No `Any`** | No `Any` in production type annotations. Use `object`, generics, or `Protocol`. |
| 2 | **Dictionary aliases** | Use `BaseDict` / `JSONDict` instead of bare `dict[str, ...]`. |
| 3 | **Immutable dataclasses** | Always `@dataclass(frozen=True, slots=True)`. Exception: `Container`. |
| 4 | **Typed docstrings** | Google-style with `"""` triple-double-quote delimiters. Imperative mood for functions/methods, noun phrase for classes. `Raises:` only for exceptions raised directly in the function body. |
| 5 | **Dead code removal** | Remove dead code in the same change-set. No commented-out blocks. |
| 6 | **No legacy shims** | No compatibility wrappers for retired patterns. |
| 7 | **Architecture boundaries** | Clean Architecture import rules enforced (see section 4). |
| 8 | **HTTP status constants** | Use `fastapi.status` instead of raw HTTP integers. |
| 9 | **No `print()`** | Use stdlib `logging` with structured `extra={...}` for all logging. |
| 10 | **Keyword-only args** | Use `*` separator when a function has 3+ parameters. |
| 11 | **Exception chaining** | Always `raise NewError(...) from original_error`. |
| 12 | **`Final` constants** | Use `Final[type]` for module-level constants; `@final` for sealed classes. |
| 13 | **No magic strings** | Extract repeated strings into `Final[str]` constants or use registry constants. |
| 14 | **Cognitive load** | Max ~4 chunks per function. Early returns, named conditionals, deep modules. |

---

## 5a. Cognitive Load

Write code for human brains. Working memory holds ~4 chunks simultaneously.

- **Deep modules over shallow** — simple interfaces hiding complex implementations.
- **Locality of behavior** — keep related code together.
- **Extract complex conditionals** — name intermediate boolean variables.
- **Early returns over nesting** — each nesting level adds a chunk.
- **Balanced DRY** — a little duplication is better than a wrong abstraction.
- **Comments for WHY** — code shows WHAT; comments explain intent.

See `.claude/rules/cognitive-load.md` for full rules.

---

## 6. Testing Conventions

### Markers and Structure

```python
@pytest.mark.unit           # Fast, isolated, no I/O
@pytest.mark.integration    # Database, API, external services
@pytest.mark.asyncio        # Async test functions
@pytest.mark.slow           # Long-running tests
```

### Requirements

- All new code must have tests.
- Use `factory-boy` for test data (`tests/factories/`).
- Use `hypothesis` for property-based testing (`tests/property/`).
- Reusable mocks go in `tests/mocks/`.
- Shared fixtures go in `tests/fixtures/` or `conftest.py`.
- Minimum 70% code coverage target.
- `freezegun` for time-dependent tests.
- `respx` for mocking httpx calls.
- `pytest-benchmark` for performance assertions.

### Running Tests

```bash
task test                # Default: backend unit + frontend unit
task test:unit           # Backend unit only
task test:integration    # Integration only
task test:property       # Hypothesis
task test:performance    # Benchmarks
task test:coverage       # With coverage report
task test:frontend       # Frontend (Vitest)
```

---

## 7. Validation Checklist

Run these before considering any change complete:

```bash
task test                # All tests pass
task lint                # No lint errors
task typecheck           # No type errors
task pre-commit          # All pre-commit hooks pass
```

For full CI-equivalent validation:

```bash
task check               # lint + test:unit + typecheck + xenon
```

---

## 8. Configuration

| Aspect | Location |
| --- | --- |
| Config factory | `ekko.config.runtime.get_config()` |
| Env var prefix | `EKKO_` (e.g. `EKKO_OPENAI_API_KEY`) |
| Settings facets | `backend/src/ekko/config/settings/*.py` (`*Settings` mixins on `ConfiguredSettings`) |
| Aggregate config | `backend/src/ekko/config/base.py` (`BaseAppConfig`) |
| Environment configs | `backend/src/ekko/config/environments/*.py` (`LocalConfig`, `DevelopmentConfig`, `ProductionConfig`, `TestingConfig`) |
| Config consumers | `from_config(cls, config: _XConfig)` with a private structural `Protocol` per component |
| Env selector | `EKKO_ENVIRONMENT` env var (defaults to `local`) |
| Dotenv loading | `.env` -> `.env.{stage}` -> `.env.local` (last wins) |
| Naming registry | `registry/naming_registry.json` -> `core/registry_constants.py` |
| Ruff config | `ruff.toml` |
| Auth | Auto-authenticates as `dev-user` (local-only, no JWT) |

---

## 9. AI Pipeline

| Component | Location | Purpose |
| --- | --- | --- |
| PII scrubber | `ai/pii/` | Regex-based anonymization before LLM calls |
| Chains | `ai/chains/` | Conversational chains (LiteLLM-backed) |
| Prompts | `ai/prompts/` | Prompt registry, templates, and versioning |
| Chat client | `infrastructure/clients/chat.py` | LiteLLM-based chat completion client |
| STT | `infrastructure/stt/` | Azure Speech speech-to-text |

### AI Dependencies

- `core/ports/` defines port protocols for all AI components.
- `ai/` may import from `core/` and `config/` only.
- `ai/` must NOT import from `application/`, `infrastructure/`, or `presentation/`.

---

## 10. Documentation Search Policy

When you need official library or framework documentation:

1. **Use Context7 tools first** -- always prefer authoritative, up-to-date docs.
2. In prompts, explicitly request: `use context7`.
3. Fall back to general model knowledge only when Context7 has no result.

---

## 11. Customization Structure

Both runtimes share one source of truth on disk — this section used to mirror
that structure as prose and drifted every time a skill, agent, or instruction
was added, renamed, or removed. Discover the current roster directly instead:

| Want to see... | Look at... |
| --- | --- |
| Claude Code CLI settings/hooks/commands | `.claude/settings.json`, `.claude/commands/`, `.claude/hooks/` |
| Claude agents | `.claude/agents/*.md` |
| Copilot agents | `.github/agents/*.agent.md` (see `.github/agents/README.md`) |
| Skills (mirrored, byte-identical) | `.github/skills/`, `.claude/skills/`, `.agents/skills/` |
| Instructions ↔ rules (paired, same scope) | `.github/instructions/*.instructions.md` ↔ `.claude/rules/*.md` |
| Copilot hooks | `.github/hooks/*.json` |
| Prompts ↔ commands | `.github/prompts/` (see its `README.md`) ↔ `.claude/commands/` |
| MCP servers (kept in parity) | `.vscode/mcp.json`, `.claude/mcp.json`, `.mcp.json` |

Validate parity and catch drift (stale paths, project-token leaks into
portable skills, MCP mismatches) with:

```bash
uv run --project backend python tools/conventions/check_agent_customizations.py
```

See the `agent-config` skill for placement rules (skill vs instruction vs
`AGENTS.md`) and the full three-tree parity contract.

## 12. Claude Code CLI vs VS Code Copilot

| Capability | Claude Code CLI (`claude`) | VS Code GitHub Copilot |
| --- | --- | --- |
| **Primary config** | `CLAUDE.md` (auto-loaded) | `.github/copilot-instructions.md` |
| **Path-scoped rules** | `.claude/rules/*.md` (`paths:`) | `.github/instructions/*.md` (`applyTo:`) |
| **Skills** | `.github/skills/` (shared, with `paths:` for auto-loading) | `.github/skills/` |
| **Agents** | `.claude/agents/` (13 agents) | `.github/agents/` (17 agents) |
| **Hooks** | `.claude/settings.json` hooks section | `.github/hooks/{tool-guardian,dependency-license-checker}.json` |
| **Shell access** | Guarded terminal (task, uv, bun; Git commands denied) | Guarded terminal tools |
| **File editing** | Direct read/write/edit tools | Inline editor suggestions |
| **Multi-file refactors** | Native (reads full tree) | Manual or via Copilot Edits |
| **Test execution** | Runs `task test` directly | Requires terminal passthrough |
| **Git operations** | Full git CLI access | Via Source Control UI |
| **MCP servers** | `.claude/mcp.json` (context7, gitnexus, playwright, shadcn) | `.vscode/mcp.json` (same 4, kept in parity) |

Both tools share skill packs in `.github/skills/` and respect `AGENTS.md`
for general conventions. `CLAUDE.md` provides CLI-specific overrides and
the authoritative instruction set for Claude Code sessions.

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **ekko** (4341 symbols, 6584 relationships, 82 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/ekko/context` | Codebase overview, check index freshness |
| `gitnexus://repo/ekko/clusters` | All functional areas |
| `gitnexus://repo/ekko/processes` | All execution flows |
| `gitnexus://repo/ekko/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/cli/SKILL.md` |

<!-- gitnexus:end -->
