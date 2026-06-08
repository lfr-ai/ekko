# Ekko Backend

Backend package for Ekko (FastAPI + Strawberry GraphQL + Clean Architecture).

## Database Runtime Modes

- `local` / `test`: SQLite backend by default.
- `dev` / `prod`: PostgreSQL backend by default.
- Override backend in any environment with `EKKO_DATABASE_BACKEND=sqlite|postgresql`.

Primary DB settings:

- `EKKO_DATABASE_PATH` (SQLite file)
- `EKKO_POSTGRESQL_HOST`, `EKKO_POSTGRESQL_PORT`, `EKKO_POSTGRESQL_NAME`
- `EKKO_POSTGRESQL_USER`, `EKKO_POSTGRESQL_PASSWORD`, `EKKO_POSTGRESQL_SSLMODE`
- Optional URL overrides:
  - `EKKO_POSTGRESQL_ASYNC_DATABASE_URL_OVERRIDE`
  - `EKKO_POSTGRESQL_SYNC_DATABASE_URL_OVERRIDE`

### Migrate local PostgreSQL data into SQLite

- Task: `task db:migrate:pg-to-sqlite`
- CLI: `uv run python -m ekko.cli.postgres_to_sqlite`
- Useful flags:
  - `--source-url` (override source PostgreSQL URL)
  - `--target-url` (override target SQLite URL)
  - `--tables users ...` (migrate selected tables only)
  - `--append` (keep existing target rows; default behavior truncates target tables)

## DuckDB Migration (existing health checks)

- DuckDB can be enabled for readiness probes over the existing SQLite database.
- Configure with:
  - `EKKO_DUCKDB_ENABLED=true|false`
  - `EKKO_DUCKDB_DATABASE_PATH=./ekko_analytics.duckdb`
- REST `/health` and GraphQL `healthReady` keep existing behavior and add optional DuckDB probe results when enabled.

## Prompt Registry / Versioning

- Runtime prompts are versioned through a registry in `src/ekko/ai/prompts/versions/registry.json`.
- Prompt snapshots are stored as immutable files in `src/ekko/ai/prompts/versions/`.
- Configure behavior with:
  - `EKKO_PROMPT_AUTO_PROVISION=true|false`
  - `EKKO_PROMPT_VERSION=vN` (optional pin for all prompts)

Provision and inspect prompt versions:

- `uv run python -m ekko.cli.prompt_registry provision`
- `uv run python -m ekko.cli.prompt_registry list`
- `uv run python -m ekko.cli.prompt_registry active`
- `uv run python -m ekko.cli.prompt_registry resolve --prompt-key summary_chunks --version v1`
- `task prompts:active`
- `task prompts:resolve -- --prompt-key summary_chunks --version v1`

Generate reproducible backtest run metadata with prompt version tags:

- `uv run python -m ekko.cli.evaluator run-name --dataset-label baseline --model-label gpt-4o`
- `uv run python -m ekko.cli.evaluator metadata --dataset-label baseline --model-label gpt-4o`

## Keploy Integration

Keploy traffic capture/replay is integrated through backend task commands with explicit runtime defaults.

Local workflow:

- `task keploy:version`
- `task keploy:record`
- `task keploy:test`
- `task keploy:report`

Optional local config-file workflow:

- `keploy config --generate --path .`
- Then run `keploy record` / `keploy test` directly with `--config-path .` if you prefer a file-driven setup.

Cloud suite workflow note (CI-friendly):

- Cloud `test-suite` execution is available in newer Keploy CLI generations.
- If you use that mode, store `KEPLOY_API_KEY` only in environment/secret stores.

Operational best practices applied:

- Filter out noisy non-business endpoints from recording (`/health`, `/metrics`).
- Use `globalNoise` to ignore volatile response headers and timing noise.
- Keep app deterministic during replay (`EKKO_DISABLE_AUDIO=true`, local SQLite backend).
- Do not commit Keploy test-set secrets (`backend/keploy/*/secret.yaml`).

Windows note:

- Keploy eBPF capabilities require WSL/Docker-backed flow on Windows; ensure prerequisites from Keploy install docs are satisfied.

## Testing Notes

- Integration database tests run against PostgreSQL via `testcontainers` (Docker required).
- Integration and E2E tests run in-process using FastAPI test clients (no manual localhost server required).
- If Docker is unavailable, container-backed integration tests are skipped.

### E2E Run Matrix

- Backend-local API e2e tests: `backend/tests/e2e/`
- Repository-level containerized API e2e tests: `tests/e2e/test_backend_api_containerized.py`
- Repository-level audio pipeline e2e tests: `tests/e2e/test_audio_pipeline.py`

Run from repository root:

- `uv run --project backend python -m pytest tests/e2e -q`

Run from `backend/`:

- `uv run python -m pytest tests/e2e -q`

See the repository root `README.md` for full project documentation.
