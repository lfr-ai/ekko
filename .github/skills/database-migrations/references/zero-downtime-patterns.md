# Zero-downtime schema change patterns

Expanded guidance beyond `SKILL.md`'s guardrails — concrete expand/contract
sequences for the schema changes that most often break a running application.

## The expand/contract pattern (the general recipe)

1. **Expand**: add the new shape alongside the old one (new nullable column,
   new table, new index) without removing anything readers/writers rely on.
2. **Migrate**: deploy application code that writes both shapes; backfill
   existing rows in a separate, batched migration or offline job.
3. **Contract**: once every reader/writer is confirmed on the new shape (a
   full deploy cycle, not just a code merge), drop the old column/table in a
   final migration.

Never collapse expand/migrate/contract into a single migration — each step
must be independently deployable and revertible.

## Renaming a column

Renaming in place breaks any in-flight process still reading the old name.

1. Expand: add the new column (nullable), keep the old one.
2. Migrate: write to both columns; backfill the new column from the old one
   in batches (`UPDATE ... WHERE id BETWEEN ... AND ...`, not one statement).
3. Contract: switch reads to the new column; a later migration drops the old
   one once nothing references it (grep the codebase first).

## Adding a NOT NULL column to a live table

1. Expand: `add_column(..., nullable=True)`.
2. Migrate: backfill in batches in a data-only migration (no schema change in
   the same file as the backfill, per the Guardrails section).
3. Contract: `alter_column(..., nullable=False)` once every row is backfilled
   — confirmed by a `COUNT(*) WHERE column IS NULL` check, not assumption.

## Adding a foreign key to an existing table

- Add the column nullable first (see above).
- Add the constraint as `NOT VALID` when the database supports it (Postgres),
  then validate it in a follow-up step (`VALIDATE CONSTRAINT`) so the initial
  migration does not lock the table for a full table scan.
- Never assume existing data satisfies the constraint — validate, don't hope.

## Adding an index on a large table

- Prefer a concurrently-built index (Postgres: `CREATE INDEX CONCURRENTLY`,
  which Alembic supports via `postgresql_concurrently=True` and requires
  `autocommit_block()`); a normal `CREATE INDEX` holds a write lock for the
  duration of the build.
- Concurrent index builds cannot run inside the same transaction as other DDL
  — keep them in their own migration.

## Dropping a column or table

Only after the contract step above confirms nothing reads it:

- Grep the ORM models, raw SQL (`sql/*.sql`), and application code for the
  column/table name first.
- Drop in its own migration, separate from any expand step for a replacement.
- `downgrade()` should recreate the shape (even empty) so a rollback does not
  leave the schema stuck — verify this is not a no-op via
  `scripts/check_migration_safety.py`.

## Related

- `scripts/check_migration_safety.py` — statically flags several of the
  anti-patterns above (direct `nullable=False`, destructive drops, empty
  `downgrade()`).
- `database.instructions.md` / `database.md` rule — SQLAlchemy/ORM conventions
  this schema serves.
