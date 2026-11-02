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
│   ├── dependencies.py     # or dependency_registry.py — pick one name per project
│   ├── exception_handlers.py
│   ├── lifespan.py
│   ├── middleware/{rate_limiter,request_context}.py
│   ├── router.py
│   └── routes/root.py      # bare '/', favicon, health/readiness probes
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
- `__main__.py`: a two-line module (`from <pkg>.main import main` +
  `if __name__ == "__main__": main()`) so the package also runs via
  `python -m <pkg>`. No template needed — copy this shape verbatim.
- **App factory** (`create_app()` returning `FastAPI`): register a `lifespan`
  (startup/shutdown + `container.dispose()`), central middleware, `app.state.container`
  and `app.state.limiter`; always mount `root.router` (bare `/`, `/favicon.ico`,
  and the health/readiness probe below); mount docs / GraphQL / `/metrics`
  conditionally.

## Middleware ordering

Starlette middleware executes outside-in for requests in *reverse*
registration order — the last `app.add_middleware(...)` call becomes the
outermost layer and runs first. Register, in order:

1. `HTTPLogger` (or equivalent request/response logging) — innermost,
   closest to routing.
2. `GZipMiddleware` (`starlette.middleware.gzip`) — compress responses above
   a `minimum_size` threshold (skip tiny responses where overhead isn't worth it).
3. `RequestBodyLimitMiddleware` (`starlette.middleware.body_limit`, built in
   to Starlette — no template needed) — reject an oversized body *before*
   GZip or the logger reads it into memory. It sends a plain-text 413 at
   the ASGI layer, bypassing `exception_handlers.py` entirely.
4. `RequestContextMiddleware` — outermost, so even a rejected request (413,
   429, ...) gets a correlated request-id response header.
5. `CORSMiddleware` (`fastapi.middleware.cors`) — add only when a
   browser-based frontend consumes this API cross-origin (a same-origin or
   server-to-server-only API should omit it entirely). When present, add it
   *first* so it wraps innermost among these five, since a preflight
   `OPTIONS` request should short-circuit before body-limit/GZip/context
   logic runs. Never pair `allow_origins=["*"]` with
   `allow_credentials=True` — list explicit origins.

## Routing

- One aggregator `APIRouter` (`presentation/api/router.py` or a `routes/__init__.py`
  export hub) that always includes `root` and includes feature routers conditionally.
- One module per resource under `presentation/api/routes/`.
- Bare, non-`/api` infrastructure routes (root `/`, `/favicon.ico`) hide
  from the OpenAPI schema — see the `api-contracts` skill's
  `include_in_schema=False` convention.
- Keep the health/readiness probe in `routes/root.py`, never a standalone
  `routes/health.py` — a single-route module has no independent business
  logic to justify the extra file. Dual-mount the one handler with a
  stacked `@router.get(...)` decorator pair: a bare, hidden `/readiness`
  (Azure Container Apps / Kubernetes probe convention) and a documented,
  tagged, rate-limited `/api/health` (what an external consumer or uptime
  monitor calls) — same function, same response, two paths, zero
  duplicated logic.

## Dependencies (Annotated-first)

- Declare typed dependency aliases and reuse them in signatures:

  ```python
  ServiceDep = Annotated[ServiceProtocol, Depends(get_service)]
  ```

- Keep the aliases in `presentation/api/dependencies.py`; never inline shared
  `Depends(...)` in handler signatures.
- Obtain the container's dependencies through a private structural
  `_DependencyProvider` Protocol — never import the concrete container
  (Structural Presentation Boundary).

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
- Copy-and-rename starting point: [`assets/logging.py.template`](assets/logging.py.template).

## Rate limiting

- Keep rate limiting at the presentation boundary:
  `presentation/api/middleware/rate_limiter.py` owns the `slowapi` limiter and
  public `RATE_LIMIT_*: Final[str]` policies; route decorators consume them and a
  global `429` handler maps failures to the API error shape.
- Copy-and-rename starting point: [`assets/rate_limiter.py.template`](assets/rate_limiter.py.template).

## Validation

- Add architecture tests for inward dependencies and app-factory smoke tests.
- Test health/readiness (both mounted paths), exception mapping, lifespan
  disposal, rate-limit wiring, and logging idempotency without testing
  third-party internals.

## Placeholders

- Keep runtime-only directories in VCS with a `.gitkeep` (e.g. `logs/.gitkeep`).

## Templates

- [`assets/app_factory.py.template`](assets/app_factory.py.template) — lifespan,
  container, limiter, and router wiring in one `create_app()`.
- [`assets/container.py.template`](assets/container.py.template) — the DI
  container itself: one frozen dataclass, one `@cached_property` per port,
  each built via `Adapter.from_config(self.config)`.
- [`assets/lifespan.py.template`](assets/lifespan.py.template) — builds the
  container, stashes it on `app.state`, and disposes it on shutdown.
- [`assets/root.py.template`](assets/root.py.template) — bare `/` and
  `/favicon.ico` plus the dual-mounted `/readiness` + `/api/health`
  probe, sharing one handler.
- [`assets/router.py.template`](assets/router.py.template) — the aggregator
  router with unconditional root (health/readiness) and conditional feature
  mounts.
- [`assets/dependencies.py.template`](assets/dependencies.py.template) — the
  Annotated dependency-alias pattern this skill requires.
- [`assets/exception_handlers.py.template`](assets/exception_handlers.py.template)
  — `register_exception_handlers(app)` mapping validation/HTTP/domain/port/generic
  exceptions (including a `*ClientPort` 502 and a `*RepositoryPort` 503) to one
  canonical JSON error envelope, with 5xx-vs-4xx log-level separation. Registers
  ONE handler per NAMED domain not-found type from the `ddd` skill's
  `assets/domain_exceptions.py.template` — never the whole stdlib `LookupError`
  family (that also swallows an accidental `KeyError`/`IndexError` bug as a
  false 404 instead of a loud 500).
- [`assets/enums.py.template`](assets/enums.py.template) — the
  `StandardErrorDetail` `StrEnum` of canonical client-facing error details,
  shared by `exception_handlers.py` and the `api-contracts` skill's
  `assets/error_responses.py.template` so the two can't silently drift apart.
- [`assets/logging.py.template`](assets/logging.py.template) — idempotent
  `configure_logging()` with a structured-extras formatter and a
  request-context filter.
- [`assets/middleware_correlation.py.template`](assets/middleware_correlation.py.template)
  — pure-ASGI request-correlation middleware binding one ID per request.
  (Request body size limiting uses Starlette's built-in
  `starlette.middleware.body_limit.RequestBodyLimitMiddleware` directly —
  no template needed.)
- [`assets/rate_limiter.py.template`](assets/rate_limiter.py.template) — the
  `slowapi` `Limiter` singleton and `RATE_LIMIT_*` policy constants consumed by
  route decorators and the `429` exception handler.
- Single-endpoint modules use the `api-contracts` skill's
  `assets/route.py.template` instead — this skill owns app-level wiring, that
  one owns per-resource route shape.

## Enforcement

- [`scripts/check_backend_wiring.py`](scripts/check_backend_wiring.py) — flags
  a presentation module importing the concrete DI container class directly
  (bypassing the `_DependencyProvider` protocol) or a route handler with an
  inline `Depends(...)` default instead of a named alias. Read-only;
  complements `import-linter` (layer-level direction only, no opinion on
  in-layer wiring). Run:
  `uv run python scripts/check_backend_wiring.py src/<pkg>/presentation`.
