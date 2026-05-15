# Ekko Backend

Backend package for Ekko (FastAPI + Strawberry GraphQL + Clean Architecture).

## Testing Notes

- Integration database tests run against PostgreSQL via `testcontainers` (Docker required).
- Integration and E2E tests run in-process using FastAPI test clients (no manual localhost server required).
- If Docker is unavailable, container-backed integration tests are skipped.

See the repository root `README.md` for full project documentation.
