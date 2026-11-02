# Architecture

Clean Architecture, enforced by import-linter on the backend and a dependency
checker on the frontend.

```text
cli -> composition -> presentation -> application -> core -> config
                              infrastructure ────────┘
                              ai ────────────────────┘
```

| Layer | Responsibility |
| --- | --- |
| `core/` | Entities, value objects, ports |
| `application/` | Use cases, DTOs |
| `infrastructure/` | Persistence, external clients |
| `ai/` | LLM chains, PII anonymization, prompts |
| `presentation/` | FastAPI + GraphQL routes |
| `composition/` | DI container, app factory |

## Stack

FastAPI, Strawberry GraphQL, SQLAlchemy/Alembic, and LiteLLM on the backend;
React 19, TypeScript, Vite, Tailwind v4, shadcn/ui, Zustand, and TanStack
Query on the frontend.

## Persistence and observability

SQLite is the desktop datastore for now; no production engine is wired in yet
(see the [roadmap](modernization-roadmap.md)). Prometheus metrics are exposed
at `/metrics`; there's no external observability stack connected.

Rate limiting and live-transcript fan-out keep their state in-process by
default, which is only correct with one replica. Set `EKKO_REDIS_URL` to share
that state across replicas (`slowapi` counters plus a Redis Pub/Sub relay in
`composition/lifespan.py`); Container Apps scales past one replica in
production, so production deployments should always set it.

## Testing

```text
backend/tests/   # unit, integration, property, database
tests/           # repository-level checks, run separately from backend/tests
frontend/tests/  # Vitest + Playwright
```

CI uploads backend and frontend coverage to Codecov on every push and pull
request to `master` (requires the `CODECOV_TOKEN` repository secret).
