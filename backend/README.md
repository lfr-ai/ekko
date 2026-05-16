# Ekko Backend

Backend package for Ekko (FastAPI + Strawberry GraphQL + Clean Architecture).

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
