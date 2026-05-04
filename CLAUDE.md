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

## 1. Project Overview

**Ekko** is an AI-powered voice assistant platform that captures desktop audio,
transcribes speech, runs AI pipelines (summarization, PII scrubbing, multi-agent
orchestration), and presents results through a local web UI.

| Attribute | Value |
| --- | --- |
| Runtime | Python 3.12, FastAPI, Uvicorn |
| ORM | SQLAlchemy 2.0+ async, aiosqlite (SQLite) |
| AI | LangChain, OpenAI, CrewAI, faster-whisper |
| GraphQL | Strawberry GraphQL (subscriptions) |
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
├── core/                # Domain entities, value objects, interfaces (ports), exceptions
│   ├── entities/        # Domain entities
│   ├── value_objects/   # Immutable value objects
│   ├── interfaces/      # Port protocols (audio, chat, embedding, llm, pii)
│   ├── exceptions/      # Domain exception hierarchy
│   ├── enums/           # Domain enumerations (base, ai, audio, messaging)
│   ├── protocols.py     # Shared protocols
│   └── registry_constants.py  # Generated naming constants
├── application/         # DTOs, handlers, services, mappers
│   ├── dtos/            # Data transfer objects
│   ├── handlers/        # Application handlers
│   ├── mappers/         # Entity <-> DTO mappers
│   └── services/        # Orchestration services (chat, summarizer)
├── infrastructure/      # Persistence (ORM, repos), clients, adapters
│   ├── adapters/        # Audio, STT adapters
│   ├── concurrency/     # QueueManager, ThreadManager
│   ├── db/              # SQLAlchemy engine, models (SQLite + aiosqlite)
│   ├── llm/             # LLM chat adapters
│   └── stt/             # Speech-to-text transcriber
├── ai/                  # AI vertical
│   ├── crewai/          # HMAS multi-agent system (YAML config)
│   ├── chains/          # Conversational chains
│   ├── embeddings/      # Embedding service
│   ├── llm/             # LLM adapter
│   ├── pii/             # PII anonymization (regex-based)
│   └── prompts/         # Prompt templates
├── presentation/        # FastAPI routes, GraphQL, middleware, DI
│   ├── api/             # REST routes, dependencies, middleware
│   └── graphql/         # Strawberry schema, queries, mutations, subscriptions
├── composition/         # DI container + app factory
├── config/              # Pydantic BaseSettings, environment-based overrides
│   └── settings/        # base.py, local.py, test_env.py + get_settings()
├── cli/                 # CLI entry points
└── utils/               # Cross-cutting: logger, helpers, types, validators
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
core -> utils -> config -> infrastructure -> application -> composition -> presentation -> main
```

Dependencies always point **inward**. Outer layers depend on inner layers, never
the reverse. The `core/` layer has zero framework imports.

### Import Rules

| Layer | May Import From | NEVER Imports From |
| --- | --- | --- |
| `utils/` | stdlib ONLY | ALL other project layers |
| `config/` | `utils/`, external libs | `presentation/`, `application/`, `core/` |
| `core/` | `utils/`, `config/` | `presentation/`, `application/`, `infrastructure/` |
| `infrastructure/` | `core/`, `config/`, `utils/`, external libs | `presentation/`, `application/` |
| `ai/` | `config/`, `utils/`, `core/` | `presentation/`, `application/`, `infrastructure/` |
| `application/` | `core/`, `infrastructure/`, `ai/`, `config/`, `utils/` | `presentation/` |
| `presentation/` | `application/`, `core/`, `config/`, `utils/` | (top layer) |

### DI Pattern

- `composition/Container` wires all dependencies using `@cached_property`.
- `presentation/api/dependencies.py` exposes FastAPI `Depends()` callables.
- Concrete classes implement protocols declared in `core/interfaces/`.

---

## 5. Hard Rules

These are non-negotiable. Every change must satisfy all of them.

| # | Rule | Details |
| --- | --- | --- |
| 1 | **No `Any`** | No `Any` in production type annotations. Use `object`, generics, or `Protocol`. |
| 2 | **Dictionary aliases** | Use `BaseDict` / `JSONDict` instead of bare `dict[str, ...]`. |
| 3 | **Immutable dataclasses** | Always `@dataclass(frozen=True, slots=True)`. Exception: `Container`. |
| 4 | **Typed docstrings** | Google-style. `Raises:` only for exceptions raised directly in the function body. |
| 5 | **Dead code removal** | Remove dead code in the same change-set. No commented-out blocks. |
| 6 | **No legacy shims** | No compatibility wrappers for retired patterns. |
| 7 | **Architecture boundaries** | Clean Architecture import rules enforced (see section 4). |
| 8 | **HTTP status constants** | Use `fastapi.status` instead of raw HTTP integers. |
| 9 | **No `print()`** | Use `structlog` for all logging. |
| 10 | **Keyword-only args** | Use `*` separator when a function has 3+ parameters. |
| 11 | **Exception chaining** | Always `raise NewError(...) from original_error`. |
| 12 | **`Final` constants** | Use `Final[type]` for module-level constants; `@final` for sealed classes. |
| 13 | **No magic strings** | Extract repeated strings into `Final[str]` constants or use registry constants. |

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
| Settings factory | `ekko.config.settings.get_settings()` |
| Env var prefix | `EKKO_` (e.g. `EKKO_OPENAI_API_KEY`) |
| Base config | `backend/src/ekko/config/settings/base.py` (`BaseAppConfig`) |
| Local config | `backend/src/ekko/config/settings/local.py` (`LocalConfig`) |
| Test config | `backend/src/ekko/config/settings/test_env.py` (`TestingConfig`) |
| Env selector | `EKKO_ENVIRONMENT` env var (defaults to `local`) |
| Dotenv loading | `.env` -> `.env.{stage}` -> `.env.local` (last wins) |
| Naming registry | `registry/naming_registry.json` -> `core/registry_constants.py` |
| Ruff config | `backend/ruff.toml` |
| Auth | Auto-authenticates as `dev-user` (local-only, no JWT) |

---

## 9. AI Pipeline

| Component | Location | Purpose |
| --- | --- | --- |
| CrewAI HMAS | `ai/crewai/` | Multi-agent orchestration (YAML config) |
| PII scrubber | `ai/pii/` | Regex-based anonymization before LLM calls |
| Chains | `ai/chains/` | LangChain conversational chains |
| Embeddings | `ai/embeddings/` | Embedding service for RAG |
| Prompts | `ai/prompts/` | Prompt template files |
| LLM adapter | `ai/llm/` | LLM adapter layer |
| STT | `infrastructure/stt/` | faster-whisper speech-to-text |

### AI Dependencies

- `core/interfaces/` defines port protocols for all AI components.
- `ai/` may import from `core/`, `config/`, `utils/` only.
- `ai/` must NOT import from `application/`, `infrastructure/`, or `presentation/`.

---

## 10. Documentation Search Policy

When you need official library or framework documentation:

1. **Use Context7 tools first** -- always prefer authoritative, up-to-date docs.
2. In prompts, explicitly request: `use context7`.
3. Fall back to general model knowledge only when Context7 has no result.

---

## 11. Customization Structure

### Claude Code CLI (`.claude/`)

```text
.claude/
├── settings.json              # Project settings: permissions (all Bash allowed), hooks, env
├── settings.local.json        # Personal overrides (gitignored)
├── agents/
│   ├── code-reviewer.md       # Code review (model: sonnet, read-only, effort: high)
│   ├── researcher.md          # Codebase exploration (model: haiku, read-only)
│   ├── test-writer.md         # Test writing (model: sonnet, effort: high)
│   ├── refactorer.md          # Refactoring (model: inherit, isolation: worktree)
│   ├── debugger.md            # Bug investigation (model: sonnet, effort: high)
│   ├── architect.md           # Architecture design (model: opus, effort: xhigh, read-only)
│   ├── frontend-reviewer.md   # Frontend review (model: sonnet, read-only)
│   └── devops.md              # Build/deploy/CI (model: sonnet)
├── hooks/
│   ├── guard-destructive.sh   # PreToolUse: block dangerous commands (Unix)
│   ├── guard-destructive.ps1  # PreToolUse: block dangerous commands (Windows)
│   ├── stop-uncommitted-reminder.sh   # Stop: warn about uncommitted files (Unix)
│   └── stop-uncommitted-reminder.ps1  # Stop: warn about uncommitted files (Windows)
├── rules/
│   ├── architecture.md        # Scoped to backend/src/ekko/**/*.py
│   ├── python-conventions.md  # Scoped to **/*.py
│   ├── testing.md             # Scoped to tests/**/*.py
│   ├── frontend.md            # Scoped to frontend/src/**/*.{ts,tsx}
│   ├── shell.md               # Scoped to **/*.{sh,ps1}
│   └── registry.md            # Scoped to registry/**
└── skills/
    ├── clean-architecture/    # Auto-loads on backend Python files
    ├── python-conventions/    # Auto-loads on all Python files
    ├── testing-conventions/   # Auto-loads on test files
    ├── frontend-react-stack/  # Auto-loads on frontend TS/TSX files
    ├── naming-registry/       # Manual invoke only
    ├── quality-gate/          # Manual invoke only
    └── deploy-check/          # Manual invoke only
```

### Claude Code Agents Reference

| Agent | Model | Tools | Isolation | Effort | Permission Mode |
| --- | --- | --- | --- | --- | --- |
| `code-reviewer` | sonnet | Read, Grep, Glob, Bash | — | high | acceptEdits |
| `researcher` | haiku | Read, Grep, Glob | — | medium | plan |
| `test-writer` | sonnet | Read, Grep, Glob, Write, Edit, Bash | — | high | acceptEdits |
| `refactorer` | inherit | Read, Grep, Glob, Write, Edit, Bash | worktree | high | acceptEdits |
| `debugger` | sonnet | Read, Edit, Bash, Grep, Glob, Write | — | high | acceptEdits |
| `architect` | opus | Read, Grep, Glob, Bash | — | xhigh | plan |
| `frontend-reviewer` | sonnet | Read, Grep, Glob, Bash | — | high | acceptEdits |
| `devops` | sonnet | Read, Grep, Glob, Bash, Write, Edit | — | high | acceptEdits |

**Usage**: Claude auto-delegates based on the `description` field. You can also
invoke explicitly: `@code-reviewer review auth changes` or run a full session
as an agent: `claude --agent code-reviewer`.

### MCP Servers

| Config file | Tool | Servers |
| --- | --- | --- |
| `.mcp.json` | Claude Code CLI | context7, shadcn, gitnexus |
| `.vscode/mcp.json` | VS Code Copilot | context7, shadcn, gitnexus |

### VS Code Copilot (`.github/`)

```text
.github/
├── copilot-instructions.md         # Global VS Code Copilot instructions
├── agents/                         # Agent definitions (9 agents)
│   ├── backend-python.agent.md     # Python backend specialist
│   ├── frontend-react.agent.md     # React frontend specialist
│   ├── expert-react-frontend-engineer.agent.md
│   ├── testing-specialist.agent.md
│   ├── database-specialist.agent.md
│   ├── security-specialist.agent.md
│   ├── debug.agent.md              # Bug investigation mode
│   ├── deep-thinking.agent.md      # Cross-cutting architecture analysis
│   └── modernization.agent.md      # Repo-wide modernization planning
├── skills/                         # Skill packs (shared by Claude + Copilot)
│   ├── clean-architecture/SKILL.md
│   ├── python-conventions/SKILL.md
│   ├── testing-conventions/SKILL.md
│   ├── frontend-react-stack/SKILL.md
│   ├── naming-registry/SKILL.md
│   ├── gitnexus/SKILL.md
│   └── openspec/SKILL.md
├── instructions/                   # File-scoped instructions (auto-load via applyTo)
│   ├── architecture.instructions.md        # backend/src/ekko/**/*.py
│   ├── coding-conventions.instructions.md  # **/*.py
│   ├── testing.instructions.md             # tests/**/*.py
│   ├── shell.instructions.md               # **/*.{sh,ps1}
│   ├── registry.instructions.md            # registry/**
│   └── update-docs-on-code-change.instructions.md  # **/*.{md,py,yml,yaml,toml,json}
├── hooks/                          # VS Code Copilot hooks
│   ├── hooks.json                  # Combined hook config
│   ├── tool-guardian.json          # PreToolUse: block destructive ops
│   └── dependency-license-checker.json  # Stop: license compliance check
├── prompts/                        # Reusable prompt templates
│   ├── review.prompt.md
│   ├── test.prompt.md
│   ├── refactor.prompt.md
│   └── debug.prompt.md
├── knowledge/
│   └── EKKO_KNOWLEDGE_GRAPH.md     # Codebase knowledge graph
└── CODEOWNERS
```

### Shared Skills (Claude Code + VS Code Copilot)

| Skill | Scope |
| --- | --- |
| **Clean Architecture** | Layer boundaries, dependency rules |
| **Python Conventions** | Naming, typing, Pydantic, logging |
| **Testing Conventions** | Pytest fixtures, factories, coverage |
| **Frontend React Stack** | React + TypeScript + Vite + shadcn/ui |
| **Naming Registry** | Registry-first constant generation |
| **GitNexus** | Graph-powered code intelligence |
| **OpenSpec** | Spec-driven planning |

---

## 12. Claude Code CLI vs VS Code Copilot

| Capability | Claude Code CLI (`claude`) | VS Code GitHub Copilot |
| --- | --- | --- |
| **Primary config** | `CLAUDE.md` (auto-loaded) | `.github/copilot-instructions.md` |
| **Path-scoped rules** | `.claude/rules/*.md` (`paths:`) | `.github/instructions/*.md` (`applyTo:`) |
| **Skills** | `.claude/skills/` + `.github/skills/` | `.github/skills/` |
| **Agents** | `.claude/agents/` (8 agents) | `.github/agents/` (9 agents) |
| **Hooks** | `.claude/settings.json` hooks section | `.github/hooks/*.json` |
| **Shell access** | Full terminal (task, git, uv, bun) | Limited via `@terminal` |
| **File editing** | Direct read/write/edit tools | Inline editor suggestions |
| **Multi-file refactors** | Native (reads full tree) | Manual or via Copilot Edits |
| **Test execution** | Runs `task test` directly | Requires terminal passthrough |
| **Git operations** | Full git CLI access | Via Source Control UI |
| **MCP servers** | `.mcp.json` | `.vscode/mcp.json` |

Both tools share skill packs in `.github/skills/` and respect `AGENTS.md`
for general conventions. `CLAUDE.md` provides CLI-specific overrides and
the authoritative instruction set for Claude Code sessions.
