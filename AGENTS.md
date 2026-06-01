# AGENTS.md

This file provides instructions for AI coding agents (GitHub Copilot, Cursor, Cline, etc.)
working within this codebase.

## Documentation and Code-Example Search Policy

- When you need official library/framework documentation, **use Context7 tools first**.
- In prompts, explicitly request these tools when relevant:
  - `use context7`
- Prefer Context7 for authoritative API/reference answers.

## OpenSpec Workflow Baseline

OpenSpec is required for non-trivial feature work and architectural changes.

- Use OpenSpec before implementation to define intent and requirements.
- Keep specs in-repo under `openspec/` as the planning source of truth.
- For default flow, use: propose → apply → sync → archive.

Recommended command path:

- `/opsx:explore` (optional, for ambiguous problems)
- `/opsx:propose <change>`
- `/opsx:apply <change>`
- `/opsx:sync <change>`
- `/opsx:archive <change>`

For expanded flow (if enabled), use `/opsx:new`, `/opsx:continue` or
`/opsx:ff`, `/opsx:verify`, `/opsx:archive`.

OpenSpec quality expectations:

- Specs must be behavior-first and testable.
- Use explicit ADDED/MODIFIED/REMOVED deltas for change specs.
- Keep implementation details in `design.md` and `tasks.md`, not in `spec.md`.
- Keep changes focused and named clearly (e.g., `add-dark-mode`,
  `fix-login-redirect`).

OpenSpec operational baseline in this repo:

- Default project schema: `openspec/schemas/ekko-production/`.
- Strict validation command: `task tools:openspec:validate`.
- Bootstrap/update OpenSpec integrations:
  - `task tools:openspec:init`
  - `task tools:openspec:update`

Tool command syntax note:

- Claude/Codex style generally uses `/opsx:<command>`.
- GitHub Copilot custom prompts in `.github/prompts/` are invoked as
  `/opsx-<command>`.

## MCP Baseline and Tool Parity

### MCP configuration sources

| File | Purpose | Read by |
| ---- | ------- | ------- |
| `.vscode/mcp.json` | VS Code runtime (authoritative for Copilot) | VS Code |
| `.claude/mcp.json` | Claude Code CLI runtime | Claude Code |

There is **no** `.mcp.json` at project root. Keeping a root-level MCP file can
cause duplicate server discovery and drift between clients.

### Required baseline MCP servers

- `context7` — authoritative, up-to-date documentation lookup
- `gitnexus` — code-graph intelligence for architecture-aware search
- `shadcn` — registry-aware component discovery and installation for frontend work

### VS Code MCP policy

- `.vscode/mcp.json` is the source of truth for workspace MCP in VS Code.
- `.vscode/settings.json` must keep:
  - `"chat.mcp.discovery.enabled": false` (avoid duplicate/discovered entries)
  - `"chat.mcp.autoStart": true` (auto-start configured MCP servers)
- Do not install duplicate marketplace MCP servers when equivalent workspace
  entries already exist.

### Agent tool parity requirement

All `.github/agents/*.agent.md` profiles must include at least:

- `'context7/*'`
- `'gitnexus/*'`

Frontend-focused agent profiles should additionally include `'shadcn/*'`.

---

## Architecture Overview

This project follows **Clean Architecture** with strict separation of concerns.
The **Dependency Rule** is the fundamental invariant: source-code dependencies always
point **inward**, never from core toward frameworks/adapters.

```text
┌─────────────────────────────────────────────────────┐
│  Presentation (API routes, middleware, DI)          │  <- FastAPI entry points
├─────────────────────────────────────────────────────┤
│  Application (orchestration, use case services)     │  <- Use case orchestration
├─────────────────────────────────────────────────────┤
│  Core (entities, value objects, domain services)    │  <- Business logic
├─────────────────────────────────────────────────────┤
│  Infrastructure (DB repos, external clients)         │  <- External integrations
├─────────────────────────────────────────────────────┤
│  AI (CrewAI HMAS, PII, chains, embeddings, RAG)    │  <- AI pipeline
├─────────────────────────────────────────────────────┤
│  Config (frozen settings, environment-specific)     │  <- Configuration
├─────────────────────────────────────────────────────┤
│  Utils (logger, common helpers, types)              │  <- Cross-cutting concerns
└─────────────────────────────────────────────────────┘
```

### Project Structure

```text
backend/src/ekko/
├── presentation/        # FastAPI routes, GraphQL, middleware, schemas
│   ├── api/             # REST routes, dependencies, middleware
│   └── graphql/         # Strawberry GraphQL schema, queries, mutations
├── application/         # Use case orchestration
│   ├── dtos/            # Data transfer objects
│   ├── handlers/        # Application handlers
│   ├── mappers/         # Entity <-> DTO mappers
│   └── services/        # Orchestration services (chat, summarizer)
├── core/                # Domain entities, value objects, business rules
│   ├── entities/        # Domain entities
│   ├── enums/           # Domain enumerations (base, ai, audio, messaging, etc.)
│   ├── exceptions/      # Domain exception hierarchy
│   ├── interfaces/      # Port protocols (audio, chat, embedding, llm, pii)
│   ├── protocols.py     # Shared protocols
│   ├── value_objects/   # Immutable value objects
│   └── registry_constants.py  # Generated naming constants
├── infrastructure/      # External integrations, persistence
│   ├── adapters/        # Audio, STT adapters
│   ├── concurrency/     # QueueManager, ThreadManager
│   ├── db/              # SQLAlchemy engine, models (SQLite + aiosqlite)
│   ├── llm/             # LLM chat adapters
│   └── stt/             # Speech-to-text transcriber
├── ai/                  # AI vertical
│   ├── chains/          # Conversational chains
│   ├── crewai/          # HMAS multi-agent system
│   ├── embeddings/      # Embedding service
│   ├── llm/             # LLM adapter
│   ├── pii/             # PII anonymization (regex-based)
│   └── prompts/         # Prompt templates
├── composition/         # DI container + app factory
├── config/              # Frozen settings, logging
├── cli/                 # CLI entry points
└── utils/               # Logger, common helpers, types

tests/
├── unit/                # Fast, isolated, no I/O
├── integration/         # Database, API, external services
├── property/            # Hypothesis property-based tests
├── performance/         # Benchmark and timing tests
├── e2e/                 # End-to-end tests
├── database/            # Migration and ORM model tests
├── factories/           # factory-boy factories
├── fixtures/            # Shared test data
├── mocks/               # Reusable mock objects
└── utils/               # Assertion helpers

frontend/src/
├── application/         # Hooks and state management (stores)
├── domain/              # Models, types, schemas (Zod)
├── infrastructure/      # API clients, config
├── lib/                 # Utilities (cn helper)
├── presentation/        # Components (ui/common/layout), pages, features, styles
└── router/              # React Router config

tasks/                   # Split Taskfile includes (backend, frontend)
tools/                   # Convention checkers and security audits
registry/                # Naming registry (JSON -> generated constants)
```

### Dependency Rule

| Layer | May Import From | NEVER Imports From |
| --- | --- | --- |
| **utils/** | stdlib ONLY | ALL other project layers |
| **config/** | utils/, external libs | presentation/, application/, core/ |
| **core/** | utils/, config/ | presentation/, application/, infrastructure/ |
| **infrastructure/** | core/, config/, utils/, external libs | presentation/, application/ |
| **ai/** | config/, utils/, core/ | presentation/, application/, infrastructure/ |
| **application/** | core/, infrastructure/, ai/, config/, utils/ | presentation/ |
| **presentation/** | application/, core/, config/, utils/ | (top layer) |

---

## Coding Standards

- **Python 3.12**, uv for dependency management, Taskfile for task running
- **FastAPI** + Uvicorn for HTTP
- **SQLAlchemy 2.0+** async ORM with aiosqlite driver (SQLite)
- **Pydantic v2** for validation with `Annotated` + `Field`
- **ruff** for linting/formatting (config in `backend/ruff.toml`), **ty** for type checking
- **structlog** for structured logging (never `print()`)
- Full type hints on all functions, methods, class attributes
- Google-style docstrings on all public APIs
- `Final` for constants, `@final` for sealed classes/methods
- Keyword-only arguments with `*` separator for 3+ params
- `frozen=True, slots=True` on all dataclasses
- Exception chaining: `raise NewError(...) from original_error`
- `bun` for frontend package management
- **Biome** for frontend linting/formatting

### String Constant Consistency

- **No hardcoded magic strings** -- extract repeated or semantically meaningful strings
  into `Final[str]` constants at the module or package level.
- Registry-generated constants (`core/registry_constants.py`) are the single source of truth
  for ORM field names, API field names, route paths, and status enums. Never duplicate them.
- Enum values must be used instead of string literals when referencing strategy names,
  status codes, or other enumerated domain values.

**Examples**:

```python
# ❌ Bad: Magic strings
user_data = {"role": "admin", "status": "active"}
response = requests.get("/api/users")

# ✅ Good: Use registry constants and enums
from ekko.core.registry_constants import FIELD_ROLE, FIELD_STATUS, ROUTE_API_USERS
from ekko.core.enums.common import UserRole, Status

user_data = {FIELD_ROLE: UserRole.ADMIN.value, FIELD_STATUS: Status.ACTIVE.value}
response = requests.get(ROUTE_API_USERS)
```

**When to use module constants vs registry constants**:

```python
# Use registry constants for cross-layer values
from ekko.core.registry_constants import FIELD_USER_ID, ROUTE_HEALTH

# Use module-level constants for implementation details
_DEFAULT_TIMEOUT: Final[int] = 30
_MAX_RETRIES: Final[int] = 3
_CACHE_KEY_PREFIX: Final[str] = "user_session"
```

**Legitimate exceptions** (documented in `tools/conventions/magic_strings_exceptions.json`):

- External API contracts (OpenAPI spec fields, third-party response keys)
- Framework limitations (Strawberry GraphQL literal defaults)
- System dict access (audio device info, getattr fallbacks)

**Enforcement**: Run `uv run python tools/conventions/check_magic_strings.py` to detect violations.

### Docstring Raises Policy

- **Only document exceptions directly raised by the function body** -- never document
  exceptions raised by called functions, dependencies, or downstream services.
- Every `raise` statement in a function must have a corresponding `Raises:` entry.
- If a function has no direct `raise` statements, omit the `Raises:` section entirely.

---

## Skill Packs (`.github/skills/`)

| Skill | Path | Scope |
| --- | --- | --- |
| **Clean Architecture** | `.github/skills/clean-architecture/SKILL.md` | Layer boundaries, dependency rules |
| **Python Conventions** | `.github/skills/python-conventions/SKILL.md` | Naming, typing, Pydantic, logging |
| **Testing Conventions** | `.github/skills/testing-conventions/SKILL.md` | Pytest fixtures, factories, coverage |
| **Frontend React Stack** | `.github/skills/frontend-react-stack/SKILL.md` | React + TypeScript + Vite + shadcn/ui |
| **Naming Registry** | `.github/skills/naming-registry/SKILL.md` | Registry-first constant generation |
| **GitNexus** | `.github/skills/gitnexus/SKILL.md` | Graph-powered code intelligence |
| **OpenSpec** | `.github/skills/openspec/SKILL.md` | Spec-driven planning |
| **Quality Gate** | `.github/skills/quality-gate/SKILL.md` | Full validation suite before finalizing changes |
| **Deploy Check** | `.github/skills/deploy-check/SKILL.md` | Pre-deployment checklist and build verification |
| **DDD** | `.github/skills/ddd/SKILL.md` | Aggregates, value objects, events, repositories, bounded contexts |
| **TDD** | `.github/skills/tdd/SKILL.md` | Red-Green-Refactor, acceptance TDD, contract testing, test pyramid |
| **SDD** | `.github/skills/sdd/SKILL.md` | Specification by Example, Given-When-Then, living documentation |

---

## Agent Hooks

| Hook | Config | Events | Purpose |
| --- | --- | --- | --- |
| **Tool Guardian** | `hooks.json` → `guard-tool.{sh,ps1}` | `PreToolUse` | Block destructive ops (rm -rf, force push, DROP TABLE) |
| **License Checker** | `hooks.json` → `check-licenses.{sh,ps1}` | `Stop` | Block copyleft / unapproved licenses |

---

## Key Commands

```bash
task dev                  # Start backend + frontend in dev mode
task install              # Install all dependencies
task test                 # Run default tests
task test:unit            # Unit tests only
task test:integration     # Integration tests
task test:property        # Property-based tests (Hypothesis)
task test:performance     # Performance benchmarks
task test:e2e             # End-to-end tests
task test:frontend        # Frontend unit tests (Vitest)
task test:coverage        # Tests with coverage reports
task lint                 # Run all linters
task format               # Format all code
task typecheck            # Type check (ty + frontend)
task xenon                # Cyclomatic complexity gate
task check                # Full quality gate
task pre-commit           # Run all pre-commit hooks
task registry:generate    # Regenerate constants from naming_registry.json
task db:migrate           # Run Alembic migrations
task build:exe            # Build standalone PyInstaller EXE
task clean                # Clean all build artifacts
```

## Configuration

- Environment settings: `backend/src/ekko/config/settings/` (base -> local/test)
- Settings factory: `get_settings()` with `EKKO_ENVIRONMENT` env var
- Naming registry: `registry/naming_registry.json` -> `backend/src/ekko/core/registry_constants.py`
- Auth: Auto-authenticates as `dev-user` (local-only app, no JWT)
- GraphQL: Strawberry schema at `/graphql` with subscriptions
- CrewAI agents: YAML config in `backend/src/ekko/ai/crewai/config/`
- PII: Regex-based anonymization in `backend/src/ekko/ai/pii/`
- Deployment: Local-only desktop EXE via PyInstaller (`task build:exe`)
