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
| ORM | SQLAlchemy 2.0+ async, dual backends: SQLite (local/test) and PostgreSQL (dev/prod) |
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
task db:migrate:pg-to-sqlite   # Copy local PostgreSQL data into SQLite

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
│   ├── db/              # SQLAlchemy engine, models (SQLite local/test + PostgreSQL dev/prod)
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
- Concrete classes implement protocols declared in `core/ports/`.

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
| Settings factory | `ekko.config.settings.get_settings()` |
| Env var prefix | `EKKO_` (e.g. `EKKO_OPENAI_API_KEY`) |
| Base config | `backend/src/ekko/config/settings/base.py` (`BaseAppConfig`) |
| Local config | `backend/src/ekko/config/settings/local.py` (`LocalConfig`) |
| Test config | `backend/src/ekko/config/settings/test_env.py` (`TestingConfig`) |
| Env selector | `EKKO_ENVIRONMENT` env var (defaults to `local`) |
| Dotenv loading | `.env` -> `.env.{stage}` -> `.env.local` (last wins) |
| Naming registry | `registry/naming_registry.json` -> `core/registry_constants.py` |
| Ruff config | `ruff.toml` |
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

- `core/ports/` defines port protocols for all AI components.
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
├── settings.json              # Project settings: permissions, hooks, env, plugins
├── settings.local.json        # Personal overrides (gitignored)
├── agents/
│   ├── architect.md           # Architecture design (model: opus, effort: xhigh, read-only)
│   ├── code-reviewer.md       # Code review (model: sonnet, read-only, effort: high)
│   ├── devops.md              # Build/deploy/CI (model: sonnet)
│   ├── frontend-reviewer.md   # Frontend review (model: sonnet, read-only)
│   ├── refactorer.md          # Refactoring (model: inherit, isolation: worktree)
│   ├── researcher.md          # Codebase exploration (model: haiku, read-only)
│   ├── sdd.md                 # SDD Given-When-Then scenarios (model: sonnet)
│   ├── tdd.md                 # TDD Red-Green-Refactor (model: sonnet)
│   └── test-writer.md         # Test writing (model: sonnet, effort: high)
├── commands/
│   ├── commit.md              # Conventional commit from staged diff
│   └── opsx/                  # OpenSpec workflow commands (11 total)
│       ├── apply.md
│       ├── archive.md
│       ├── bulk-archive.md
│       ├── continue.md
│       ├── explore.md
│       ├── ff.md
│       ├── new.md
│       ├── onboard.md
│       ├── propose.md
│       ├── sync.md
│       └── verify.md
├── hooks/
│   ├── guard-destructive.sh   # PreToolUse: block dangerous commands (Unix)
│   ├── guard-destructive.ps1  # PreToolUse: block dangerous commands (Windows)
│   ├── stop-uncommitted-reminder.sh   # Stop: warn about uncommitted files (Unix)
│   └── stop-uncommitted-reminder.ps1  # Stop: warn about uncommitted files (Windows)
└── rules/
    ├── architecture.md        # Scoped to backend/src/ekko/**/*.py
    ├── python-conventions.md  # Scoped to **/*.py
    ├── testing.md             # Scoped to tests/**/*.py
    ├── frontend.md            # Scoped to frontend/src/**/*.{ts,tsx}
    ├── shell.md               # Scoped to **/*.{sh,ps1}
    ├── registry.md            # Scoped to registry/**
    ├── ddd.md                 # Scoped to core/**/*.py + application/**/*.py
    ├── tdd.md                 # Scoped to tests/**/*.py
    ├── sdd.md                 # Scoped to docs/specs/**/*.md
    ├── cognitive-load.md      # Scoped to **/*.py
    └── docs-sync.md           # Scoped to **/*.{md,py,yml,yaml,toml,json}
```

### Claude Code Agents Reference

| Agent | Model | Tools | Isolation | Effort | Permission Mode |
| --- | --- | --- | --- | --- | --- |
| `architect` | opus | Read, Grep, Glob, Bash | — | xhigh | plan |
| `code-reviewer` | sonnet | Read, Grep, Glob, Bash | — | high | acceptEdits |
| `devops` | sonnet | Read, Grep, Glob, Bash, Write, Edit | — | high | acceptEdits |
| `frontend-reviewer` | sonnet | Read, Grep, Glob, Bash | — | high | acceptEdits |
| `refactorer` | inherit | Read, Grep, Glob, Write, Edit, Bash | worktree | high | acceptEdits |
| `researcher` | haiku | Read, Grep, Glob | — | medium | plan |
| `test-writer` | sonnet | Read, Grep, Glob, Write, Edit, Bash | — | high | acceptEdits |
| `tdd` | sonnet | Read, Write, Edit, Glob, Grep, Bash | — | high | acceptEdits |
| `sdd` | sonnet | Read, Write, Edit, Glob, Grep, Bash | — | high | acceptEdits |

**Usage**: Claude auto-delegates based on the `description` field. You can also
invoke explicitly: `@code-reviewer review auth changes` or run a full session
as an agent: `claude --agent code-reviewer`.

### MCP Servers

| Config file | Tool | Servers |
| --- | --- | --- |
| `.claude/mcp.json` | Claude Code CLI | context7, shadcn, gitnexus |
| `.vscode/mcp.json` | VS Code Copilot | context7, shadcn, gitnexus |

### VS Code Copilot (`.github/`)

```text
.github/
├── copilot-instructions.md         # Global VS Code Copilot instructions
├── agents/                         # Agent definitions (13 agents)
│   ├── backend-python.agent.md     # Python backend specialist
│   ├── frontend-react.agent.md     # React frontend specialist
│   ├── testing.agent.md            # Testing strategies
│   ├── database.agent.md           # SQLAlchemy, Alembic, repository pattern
│   ├── security.agent.md           # OWASP, auth, vulnerability prevention
│   ├── debug.agent.md              # Bug investigation mode
│   ├── deep-thinking.agent.md      # Cross-cutting architecture analysis
│   ├── modernization.agent.md      # Repo-wide modernization planning
│   ├── ddd.agent.md                # DDD domain modeling expert
│   ├── tdd.agent.md                # TDD Red-Green-Refactor specialist
│   ├── sdd.agent.md                # SDD Given-When-Then scenarios
│   ├── refactor.agent.md           # Code refactoring (Fowler's catalog)
│   └── devops.agent.md             # CI/CD, Docker, infrastructure
├── skills/                         # Skill packs (shared by Claude + Copilot)
│   ├── clean-architecture/SKILL.md
│   ├── python-conventions/SKILL.md
│   ├── testing-conventions/SKILL.md
│   ├── frontend-react-stack/SKILL.md
│   ├── naming-registry/SKILL.md
│   ├── gitnexus/SKILL.md
│   ├── openspec/SKILL.md
│   ├── quality-gate/SKILL.md
│   ├── deploy-check/SKILL.md
│   ├── dry-refactoring/SKILL.md
│   ├── ddd/SKILL.md
│   ├── tdd/SKILL.md
│   └── sdd/SKILL.md
├── instructions/                   # File-scoped instructions (auto-load via applyTo)
│   ├── architecture.instructions.md        # backend/src/ekko/**/*.py
│   ├── coding-conventions.instructions.md  # **/*.py
│   ├── cognitive-load.instructions.md      # **/*.py
│   ├── testing.instructions.md             # tests/**/*.py
│   ├── shell.instructions.md               # **/*.{sh,ps1}
│   ├── registry.instructions.md            # registry/**
│   ├── update-docs-on-code-change.instructions.md  # **/*.{md,py,yml,yaml,toml,json}
│   ├── ddd.instructions.md                 # backend/src/ekko/core/**/*.py
│   ├── tdd.instructions.md                 # tests/**/*.py
│   └── sdd.instructions.md                 # docs/specs/**/*.md
├── hooks/                          # VS Code Copilot hooks
│   ├── tool-guardian.json          # PreToolUse: block dangerous commands
│   ├── dependency-license-checker.json  # Stop: license compliance
│   └── scripts/                    # Hook implementation scripts
│       ├── guard-tool.{sh,ps1}     # Block destructive commands
│       └── check-licenses.{sh,ps1} # License compliance check
├── prompts/                        # Reusable prompt templates
│   ├── review.prompt.md
│   ├── test.prompt.md
│   ├── refactor.prompt.md
│   ├── debug.prompt.md
│   ├── opsx-apply.prompt.md
│   ├── opsx-archive.prompt.md
│   ├── opsx-bulk-archive.prompt.md
│   ├── opsx-continue.prompt.md
│   ├── opsx-explore.prompt.md
│   ├── opsx-ff.prompt.md
│   ├── opsx-new.prompt.md
│   ├── opsx-onboard.prompt.md
│   ├── opsx-propose.prompt.md
│   ├── opsx-sync.prompt.md
│   └── opsx-verify.prompt.md
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
| **Quality Gate** | Full validation suite before finalizing changes |
| **Deploy Check** | Pre-deployment checklist and build verification |
| **DDD** | Aggregates, value objects, domain events, repositories, bounded contexts |
| **TDD** | Red-Green-Refactor cycle, acceptance TDD, contract testing, test pyramid |
| **SDD** | Specification by Example, Given-When-Then, living documentation |

---

## 12. Claude Code CLI vs VS Code Copilot

| Capability | Claude Code CLI (`claude`) | VS Code GitHub Copilot |
| --- | --- | --- |
| **Primary config** | `CLAUDE.md` (auto-loaded) | `.github/copilot-instructions.md` |
| **Path-scoped rules** | `.claude/rules/*.md` (`paths:`) | `.github/instructions/*.md` (`applyTo:`) |
| **Skills** | `.github/skills/` (shared, with `paths:` for auto-loading) | `.github/skills/` |
| **Agents** | `.claude/agents/` (9 agents) | `.github/agents/` (13 agents) |
| **Hooks** | `.claude/settings.json` hooks section | `.github/hooks/{tool-guardian,dependency-license-checker}.json` |
| **Shell access** | Full terminal (task, git, uv, bun) | Limited via `@terminal` |
| **File editing** | Direct read/write/edit tools | Inline editor suggestions |
| **Multi-file refactors** | Native (reads full tree) | Manual or via Copilot Edits |
| **Test execution** | Runs `task test` directly | Requires terminal passthrough |
| **Git operations** | Full git CLI access | Via Source Control UI |
| **MCP servers** | `.claude/mcp.json` | `.vscode/mcp.json` |

Both tools share skill packs in `.github/skills/` and respect `AGENTS.md`
for general conventions. `CLAUDE.md` provides CLI-specific overrides and
the authoritative instruction set for Claude Code sessions.

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **voice-bot** (4237 symbols, 6530 relationships, 65 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

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
| `gitnexus://repo/voice-bot/context` | Codebase overview, check index freshness |
| `gitnexus://repo/voice-bot/clusters` | All functional areas |
| `gitnexus://repo/voice-bot/processes` | All execution flows |
| `gitnexus://repo/voice-bot/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
