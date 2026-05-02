---
description: Warp Agent Mode project rules for Ekko
---

# Ekko — Warp Agent Rules

## Architecture

This project follows **Clean Architecture** with strict dependency rules:

- `core/` contains domain entities/value objects/interfaces and stays framework-free.
- `application/` orchestrates use-cases and depends on inward layers.
- `infrastructure/` implements ports from `core/interfaces/`.
- `presentation/` is the outer adapter layer (FastAPI routes + GraphQL).

Dependency direction is strictly inward.

## Stack

- Backend: Python 3.12+, FastAPI, SQLAlchemy async, Alembic, uv
- Frontend: React 19, TypeScript, Vite, Bun, Tailwind CSS v4
- Task runner: Taskfile (`task` commands)

## High-value commands

- `task dev` — run backend + frontend
- `task test` — run default tests
- `task lint` — run linters
- `task typecheck` — backend + frontend type checks
- `task check` — quality gate
- `task verify` — local CI parity verification

## Conventions

- Never use `print()` in Python; use structlog.
- Keep type annotations complete.
- Keep layer boundaries intact.
- Prefer minimal, scoped changes and update docs when behavior changes.
