---
name: backend-structure
description: Enforce the FastAPI backend project structure — app factory, aggregator router, Annotated dependency aliases, DI container with dispose, config facets, stdlib logging, slowapi rate limiting, and .gitkeep placeholders. Use when scaffolding a backend, adding routes/services/config, or reviewing backend layout.
---

# Backend project structure (FastAPI + Clean Architecture)

## Minimal tree

```text
src/<pkg>/
├── main.py
├── core/                  # domain types, policies, ports
├── application/           # use cases and orchestration
├── infrastructure/        # adapters, persistence, clients, logging.py
├── composition/           # container and optional app factory
├── presentation/api/
│   ├── dependencies.py
│   ├── exception_handlers.py
│   ├── lifespan.py
│   ├── middleware/rate_limiter.py
│   ├── router.py
│   └── routes/health.py
└── configs/               # settings facets + environment resolution
```

Start with one deep module per concern (`logging.py`, `rate_limiter.py`); promote
it to a package only when multiple cohesive submodules are genuinely needed.

## Layers (`src/<pkg>/`)

`core` → `application` → `infrastructure` / `presentation` → `composition` →
`main`. Dependencies always flow inward. Configuration lives in a config package.

## Entry & assembly

- `main.py`: process entry plus `create_app()`, or delegate to
  `composition/app_factory.py` when assembly is large enough to justify it.
  Run Uvicorn with an import string and `factory=True`.
- **App factory** (`create_app()` returning `FastAPI`): register a `lifespan`
  (startup/shutdown + `container.dispose()`), central middleware, `app.state.container`
  and `app.state.limiter`; always mount `/health`; mount docs / GraphQL / `/metrics`
  conditionally.

## Routing

- One aggregator `APIRouter` (`presentation/api/router.py` or a `routes/__init__.py`
  export hub) that always includes health and includes feature routers conditionally.
- One module per resource under `presentation/api/routes/`.

## Dependencies (Annotated-first)

- Declare typed dependency aliases and reuse them in signatures:

  ```python
  ServiceDep = Annotated[ServiceProtocol, Depends(get_service)]
  ```

- Keep the aliases in `presentation/api/dependencies.py`; never inline shared
  `Depends(...)` in handler signatures.

## Composition / DI

- A single container built with `from_config(cls, config)`; ports typed as
  `Protocol`; lazy services may use `@cached_property` on a non-slotted container;
  `dispose()` releases async resources at shutdown.

## Configuration

- `*Settings` facets (one cohesive group each, `env_prefix="<PKG>_"`, frozen) compose
  into an aggregate `AppConfig`; per-environment subclasses; a runtime resolver selects
  the class (env var → hostname map → local).

## Logging

- Keep logging in `infrastructure/logging.py`: stdlib `logging` +
  `TimedRotatingFileHandler`; a formatter appends structured `key=value` extras;
  a filter injects request context. Configure once before app construction, clear
  existing root handlers for idempotency, and leave domain code framework-free.

## Rate limiting

- Keep rate limiting at the presentation boundary:
  `presentation/api/middleware/rate_limiter.py` owns the `slowapi` limiter and
  public `RATE_LIMIT_*: Final[str]` policies; route decorators consume them and a
  global `429` handler maps failures to the API error shape.

## Validation

- Add architecture tests for inward dependencies and app-factory smoke tests.
- Test health, exception mapping, lifespan disposal, rate-limit wiring, and
  logging idempotency without testing third-party internals.

## Placeholders

- Keep runtime-only directories in VCS with a `.gitkeep` (e.g. `logs/.gitkeep`).
