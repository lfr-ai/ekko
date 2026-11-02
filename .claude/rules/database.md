---
paths:
  - "**/*.sql"
  - "alembic/**/*.py"
  - "src/**/infrastructure/persistence/**/*.py"
---

# Database conventions

## Boundaries and ownership

- Read the active database and migration tools from `PROJECT.md`; do not add a
  second database, ORM, query builder, or migration system speculatively.
- Keep database drivers, ORM models, SQLAlchemy sessions, and concrete
  repositories in infrastructure. Inner layers define persistence ports and
  domain-shaped records without importing persistence frameworks.
- Give each logical operation one explicit transaction owner. Do not mix hidden
  repository commits with an outer unit of work or add a second commit/rollback
  boundary. Preserve the established owner until an intentional migration updates
  every caller and integration test together.

## Sessions and transactions

- Scope a SQLAlchemy `Session` to one request, job, or command and close it
  deterministically with a context manager. Keep transactions short.
- Never share `Session` across threads or `AsyncSession` across concurrent tasks;
  use one session per thread/task.
- Roll back a failed transaction before reusing a session. Do not catch a
  database exception and continue with an inactive session.
- Use SQLAlchemy 2-style `select()`, `Session.scalars()`, and `Session.execute()`.
  Load only the rows and columns the operation needs; avoid accidental N+1 loads.

## Query safety and portability

- Bind every value through SQLAlchemy expressions or driver parameters. Never
  interpolate values into SQL with f-strings, `%`, `.format()`, or concatenation.
  Dynamic identifiers require a closed allowlist because bind parameters cannot
  represent identifiers.
- Make pagination and latest-row queries deterministic with a complete
  `ORDER BY`, including a stable unique tie-breaker.
- Derive indexes from measured query and constraint needs. Use `EXPLAIN`/
  `EXPLAIN ANALYZE` against representative data before performance claims; do not
  add speculative indexes.
- Prefer standard SQL/SQLAlchemy constructs. Use dialect-specific features only
  when `PROJECT.md` selects that database and the benefit is tested. SQLite is a
  separate dialect, not an automatic behavioral substitute for PostgreSQL.
- Keep credentials and full connection URLs out of source, logs, errors, and
  generated artifacts. Configuration comes from the typed settings boundary.

## Schema and migrations

- Treat Alembic autogeneration as a candidate diff. Review types, nullability,
  defaults, constraints, indexes, foreign-key actions, renames, data loss, lock
  duration, and both upgrade and downgrade paths.
- Never edit an applied migration. Publish a new revision; separate schema
  changes from long-running backfills and use expand/backfill/contract for live
  incompatible changes.
- Name tables, columns, indexes, and constraints consistently in lowercase
  `snake_case`. Prefer explicit constraint names so migration diffs are stable.
- Do not duplicate application defaults as server defaults unless the database
  must enforce the value for every writer. Store instants consistently in UTC.
- Run the project-native migration drift check after ORM changes and test both
  upgrade and downgrade where the migration is reversible.

## Standalone SQL

- Start mutating maintenance scripts with a clear target and make destructive
  scope visible. Use transactions when the operation supports them and fail on
  the first SQL error.
- Make seed/sync scripts idempotent when they are expected to be rerun. Document
  intentionally one-shot or irreversible operations next to the statement.
- Avoid `SELECT *` in production queries and scripts whose result shape is a
  contract; enumerate columns so schema additions cannot silently change it.
- Run `task lint:sql` (SQLFluff) before committing standalone `sql/*.sql`
  changes; it also runs as a pre-commit hook.
