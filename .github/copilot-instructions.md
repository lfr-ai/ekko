---
description: Repository development conventions for Ekko
applyTo: "**"
---

# Ekko — Development Instructions

## Architecture and Boundaries

- Follow Clean Architecture dependency direction: `presentation/infrastructure -> application -> core`.
- `backend/src/ekko/core/` must remain framework-independent — no imports from infrastructure/presentation.
- `backend/src/ekko/application/` can import from `core` and configuration, but not concrete adapters.
- `backend/src/ekko/infrastructure/` implements protocols declared in `core/interfaces/`.
- `backend/src/ekko/composition/` wires everything together via the `Container` DI pattern.
- `backend/src/ekko/presentation/api/routes/` contains FastAPI routers (health, stream).
- `backend/src/ekko/presentation/graphql/` contains Strawberry GraphQL schema, resolvers, subscriptions.
- `backend/src/ekko/ai/` contains CrewAI agents, PII anonymization, chains, embeddings, prompts.

## Backend Stack

- Python 3.12+, FastAPI, Pydantic, SQLAlchemy, Alembic, Strawberry GraphQL
- Settings: `ekko.config.settings.get_settings()` — env-specific subclasses of `BaseAppConfig`
- Enums: `ParseableEnum(StrEnum)` + `@unique` + `auto()` in `ekko.core.enums/` (split by domain)
- DI Container: `ekko.composition.Container` with `@cached_property`
- CrewAI: YAML-based agent/task config in `backend/src/ekko/ai/crewai/config/`
- PII: Regex-based anonymization in `backend/src/ekko/ai/pii/` — scrubs before LLM calls
- Testing: pytest, hypothesis, factory-boy, pytest-asyncio, pytest-benchmark
- Naming registry: `registry/naming_registry.json` -> generated constants
- Linting: ruff (config in `backend/ruff.toml`), ty for type checking

## Frontend Stack

- React 19, TypeScript, Vite 6 + SWC, Bun
- UI: shadcn/ui (Radix + Tailwind CSS v4) — use CLI, never copy-paste
- Storybook: component stories with interaction testing
- State: Zustand, TanStack React Query
- Linting: Biome (not Prettier/ESLint)
- Testing: Vitest + React Testing Library + fast-check, Playwright for E2E
- See `.github/skills/frontend-react-stack/SKILL.md` for full conventions

## Project Layout

- `tasks/` — Split Taskfile includes (backend.yml, frontend.yml)
- `tools/` — Convention checkers and security audits
- `registry/` — Naming registry JSON + code generator

## Tooling and Commands

- Use `uv` for Python dependency and command execution.
- Use `bun` for frontend package management and scripts.
- Root `Taskfile.yml` orchestrates via includes from `tasks/`.
- Run `task check` (lint + tests + typecheck) before finalizing changes.

## Quality Rules

- Keep changes minimal and scoped.
- Update docs in the same change when behavior or setup changes.
- Use typed Python signatures and avoid `Any` unless truly unavoidable.
- Use `Final[type]` for module-level constants.
- Use `@dataclass(frozen=True, slots=True)` for all dataclasses (except `Container`).
- Docstring `Raises:` sections must only document exceptions directly raised in that function body.
- Use `cn()` for Tailwind class merging, semantic color tokens only.

## Security Rules

- Never commit secrets.
- Keep `.env.example` updated when new environment variables are introduced.
- Use `detect-secrets` via pre-commit hooks.
