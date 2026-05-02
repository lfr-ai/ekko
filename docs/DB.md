# Database and Migrations

Ekko uses **SQLite** via SQLAlchemy async ORM (`aiosqlite`) with Alembic for schema migrations.

## Database Location

| Mode | Path |
|---|---|
| Development | `./ekko.db` (project root) |
| EXE (frozen) | `%LOCALAPPDATA%/ekko/ekko.db` |

## Key Files

- `backend/src/ekko/infrastructure/db/engine.py` — async engine factory
- `backend/src/ekko/infrastructure/db/models/` — SQLAlchemy ORM models
- `backend/alembic/` — Alembic configuration and migration scripts

## Run Migrations

```bash
task db:migrate
```

Or directly:

```bash
cd backend && uv run alembic upgrade head
```
