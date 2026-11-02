# Ekko Backend

Backend package for Ekko (FastAPI + Strawberry GraphQL + Clean Architecture).

## Database

SQLite with async via `aiosqlite`. WAL mode and foreign keys enabled automatically.

- `EKKO_DATABASE_PATH` — SQLite file path (default: `./ekko.db`)
- Migrations: `task db:migrate` (Alembic)

## Analytics pattern (optional): SQLite + Parquet + DuckDB

Runtime storage is SQLite only. Health checks (`/health`, `/ready`) validate
application state and SQLite connectivity.

For analytics workloads, use a file-based pattern:

1. Export query results to Parquet files.
2. Analyze Parquet files with DuckDB when needed.

Example DuckDB query pattern:

- `SELECT * FROM read_parquet('analytics/*.parquet');`

This keeps OLTP/runtime concerns on SQLite and analytical scanning on Parquet.

## API surface

- REST is the canonical transport for commands and health:
  - `GET /health` and `GET /ready` report application and SQLite state.
  - `POST /stream/start` and `POST /stream/pause` control audio streaming.
  - `POST /pii/anonymize` redacts sensitive text.
  - `GET /transcripts/stream` streams live transcript segments over SSE.
- GraphQL exposes one read-only query, `promptCatalog`, at `POST /graphql` for
  field-selective prompt browsing.
- The retired `/start_stream` and `/pause_stream` paths return `404`.

## Prompt Registry / Versioning

- Runtime prompts are versioned through closed named sets in `src/ekko/ai/prompts/registry/prompt_registry.json`.
- Prompt snapshots are stored as immutable files in `src/ekko/ai/prompts/versions/`.
- Runtime selection belongs to environment settings, never to the manifest:
  local uses editable `experimental` templates, development uses `development`,
  and production uses `production`.
- Configure behavior with:
  - `EKKO_PROMPT_AUTO_PROVISION=true|false` (authoring CLI only)
  - `EKKO_PROMPT_VERSION=vN.N` (optional immutable pin for all prompts)
  - `EKKO_PROMPT_VERSION_SET=experimental|development|production`

Active prompts:

- `summary_chunks` — chunked transcript summarization
- `summarizer_system` — system prompt for the summarizer
- `conversational_system` — conversational assistant system prompt

All templates live as flat files under `src/ekko/ai/prompts/templates/`.

Provision and inspect prompt versions:

```bash
uv run python -m ekko.cli.prompt_registry provision
uv run python -m ekko.cli.prompt_registry list
uv run python -m ekko.cli.prompt_registry active
```

## Testing Notes

- Integration database tests run against in-memory SQLite.
- Integration and E2E tests run in-process using FastAPI test clients (no manual localhost server required).

### E2E Run Matrix

- Backend-local API e2e tests: `backend/tests/e2e/`
- Repository-level containerized API e2e tests: `tests/e2e/test_backend_api_containerized.py`
- Repository-level audio pipeline e2e tests: `tests/e2e/test_audio_pipeline.py`

Run from repository root:

- `uv run --project backend python -m pytest tests/e2e -q`

Run from `backend/`:

- `uv run python -m pytest tests/e2e -q`

See the repository root `README.md` for full project documentation.
