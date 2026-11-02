---
name: database-migrations
description: Create and apply Alembic schema migrations safely — autogenerate from ORM models, review, apply, test the downgrade, and guard against drift. Use when changing the database schema, adding a migration, or resolving model/migration drift.
---

# Database migrations (Alembic)

Schema is versioned with Alembic. The migration environment reads the same
`*Settings` configuration the app uses, so credentials never diverge. Task
commands wrap the raw `alembic` calls; project-specific connection variables live
in `PROJECT.md`.

## Workflow

1. Edit the ORM models in the persistence layer (see
   [`assets/orm_model.py.template`](assets/orm_model.py.template) for a new
   table, paired with
   [`assets/repository_impl.py.template`](assets/repository_impl.py.template)
   implementing the `ddd` skill's repository port).
2. Autogenerate: `task db:revision "short_message"`.
3. **Review the generated file** — never trust autogenerate blindly. Check column
   types, nullability, indexes, foreign-key cascades, and constraints.
4. Render upgrade SQL without changing a database: `task db:upgrade:sql`.
5. Guard drift: `task db:check` fails when models and migrations disagree; run it
   in CI.
6. Hand application, downgrade testing, and stamping to a human or separately
   controlled migration identity; agents never run those state-changing tasks.

## Guardrails

- Never edit or delete an applied migration — publish a new one instead.
- Agent database credentials are read-only. Never run upgrade, downgrade, stamp,
  data backfill, sync, DDL, or DML against any database.
- Keep schema changes and data backfills in separate migrations.
- Migration files are timestamped and immutable once merged.
- Add a column to a live table as nullable (or with a default), backfill in a
  separate step, then tighten to non-nullable.

See the project's migration guide (`docs/database-migrations.md`) for the full
reference.

## Templates and references

- [`assets/orm_model.py.template`](assets/orm_model.py.template) — a
  `Mapped`/`mapped_column` table definition with a created-on timestamp mixin.
- [`assets/repository_impl.py.template`](assets/repository_impl.py.template) —
  a concrete repository implementing the `ddd` skill's repository port,
  converting each ORM row to a frozen read-only snapshot before it crosses
  the port boundary.
- [`scripts/check_migration_safety.py`](scripts/check_migration_safety.py) —
  read-only AST scan of a migration file for destructive ops applied without a
  safeguard, a column tightened to `nullable=False` in one step, or an empty
  `downgrade()`. Run: `uv run python scripts/check_migration_safety.py
  alembic/versions/<file>.py`.
- [`references/zero-downtime-patterns.md`](references/zero-downtime-patterns.md)
  — expand/contract sequences for renaming a column, adding a `NOT NULL`
  column, adding a foreign key or index to a live table, and dropping a
  column/table safely.
