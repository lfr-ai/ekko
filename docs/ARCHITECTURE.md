# Architecture

Ekko follows **Clean Architecture** with strict layer boundaries.

## Layers

```text
presentation/infrastructure -> application -> core
```

| Layer | Location | Responsibility |
|---|---|---|
| **Core** | `backend/src/ekko/core/` | Entities, value objects, enums, interfaces, exceptions |
| **Application** | `backend/src/ekko/application/` | Use cases, DTOs, mappers, orchestration services |
| **Infrastructure** | `backend/src/ekko/infrastructure/` | DB (SQLite/SQLAlchemy), OpenAI client, STT, audio streaming |
| **Presentation** | `backend/src/ekko/presentation/` | FastAPI REST routes, Strawberry GraphQL, middleware |
| **AI** | `backend/src/ekko/ai/` | CrewAI HMAS agents, PII anonymization, chains, embeddings |
| **Composition** | `backend/src/ekko/composition/` | DI container, app factory |
| **Config** | `backend/src/ekko/config/` | Pydantic settings, logging config |

## Database

SQLite via SQLAlchemy async (`aiosqlite`). Alembic manages migrations.

- Dev: `./ekko.db` (project root)
- EXE: `%LOCALAPPDATA%/ekko/ekko.db`

## Deployment

Local-only desktop application built with PyInstaller (`task build:exe`).
The EXE bundles the frontend as static files and serves them via FastAPI.
