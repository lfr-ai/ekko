# Database and migrations

This project uses SQLAlchemy for ORM models and Alembic for schema migrations.

## Key files

- `src/voice/infrastructure/db/session.py` - engine and session factory
- `src/voice/infrastructure/db/base.py` - declarative Base for models
- `alembic/` - Alembic configuration and migration scripts

## Run migrations locally

```bash
uv run alembic upgrade head
```

When deploying to production, set `DATABASE_URL` to your production
Postgres DSN and run migrations as part of your release process.
