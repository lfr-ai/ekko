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

1. Edit the ORM models in the persistence layer.
2. Autogenerate: `task db:revision "short_message"`.
3. **Review the generated file** — never trust autogenerate blindly. Check column
   types, nullability, indexes, foreign-key cascades, and constraints.
4. Apply: `task db:migrate`.
5. Test the downgrade: `task db:migrate:downgrade`, then re-apply `task db:migrate`.
6. Guard drift: `task db:check` fails when models and migrations disagree; run it
   in CI.

## Guardrails

- Never edit or delete an applied migration — publish a new one instead.
- Keep schema changes and data backfills in separate migrations.
- Migration files are timestamped and immutable once merged.
- Add a column to a live table as nullable (or with a default), backfill in a
  separate step, then tighten to non-nullable.

See the project's migration guide (`docs/database-migrations.md`) for the full
reference.
