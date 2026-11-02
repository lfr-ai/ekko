---
name: api-contracts
description: Design, evolve, and verify HTTP API contracts for REST/FastAPI/OpenAPI, Swagger UI, Postman, or GraphQL. Use when adding endpoints, changing request/response schemas, versioning an API, or reviewing contract compatibility.
---

# API contracts

Treat the published contract as a compatibility boundary. Keep transport code in
presentation and business rules behind application/domain ports.

## Workflow

1. Identify consumers, authentication, idempotency, pagination, rate limits, and
   compatibility constraints before choosing an endpoint shape.
2. Model stable resource nouns and HTTP semantics: methods, status codes,
   headers, cache behavior, and one documented error envelope.
3. Define typed request/response schemas at the boundary. Do not expose ORM or
   domain entities directly.
4. Generate OpenAPI from the application and inspect operation IDs, security
   schemes, examples, nullability, formats, and reusable components. Run the
   repository's documented API lint task with Redocly (`redocly.yaml`) against
   that same generated contract for structural findings that behavioral tests
   do not check. Keep the exact task name in `PROJECT.md` and run it as a
   merge-blocking CI gate, not a pre-commit hook, because `bunx` needs network
   access.
5. Add contract tests for success, validation, authorization, not-found,
   conflict, rate-limit, and unexpected-failure behavior.
6. Update Postman or other maintained client artifacts only when they are an
   owned contract source; avoid hand-maintained duplicates of generated OpenAPI.
7. Compare the schema with the previous release and document intentional
   breaking changes, migration, and deprecation windows.

## FastAPI and Swagger

- Use an app factory, aggregator router, and typed dependency aliases; follow
  the `backend-structure` skill.
- Declare the response shape once, as the handler's return-type annotation
  (a typed Pydantic model, never `dict`/`JSONDict` for a real resource
  endpoint) — FastAPI derives `response_model`, response validation, and the
  OpenAPI schema from that annotation automatically. Do **not** additionally
  pass a redundant `response_model=` kwarg that repeats the same type: two
  declarations of the same shape can drift out of sync with each other,
  which a single return-type annotation cannot. Reserve the `response_model=`
  kwarg for the rare case where the wire response genuinely differs from the
  return type (e.g. deliberately returning a broader internal type but
  publishing a narrower public schema). `task api:check-response-models`
  (`scripts/check_response_model_redundancy.py`, also a pre-commit hook and
  part of `task guard`) mechanically flags a `response_model=` that repeats
  the return-type annotation verbatim.
- Keep `/docs`, `/redoc`, and `/openapi.json` configurable. Public production
  exposure is a security decision, not a default.
- Give operations stable IDs if generated clients depend on them.
- Validate examples and security requirements; a rendered Swagger page is not a
  substitute for contract tests.
- When a consumer needs a shareable static API reference outside the running
  app's `/redoc` route, provide a repository task that runs Redocly
  `build-docs` and writes to a gitignored output path.
- Hide non-`/api` infrastructure routes (bare `/`, `/favicon.ico`, and
  similar browser/deploy-tooling endpoints, as opposed to `/api/*` business
  routes) from the schema with `include_in_schema=False`, and state that
  convention once in the module's docstring. Once a route is hidden,
  `responses=`, `summary=`, and `description=` on it are dead code — every
  one of those kwargs exists purely to shape the generated OpenAPI document,
  and a hidden operation is never rendered anywhere.
- For a status code that carries no body (204, 304), declare `status_code=`
  once, on the decorator, and return `None` (or omit the return) instead of
  also constructing a `Response(status_code=204)`. FastAPI empties the
  response body itself for any status that disallows one, so building the
  `Response` by hand only duplicates the single source of truth.

## REST and GraphQL

Prefer REST for resource-oriented operations unless GraphQL solves a verified
consumer need such as client-directed graph-shaped reads. If GraphQL is present:

- keep resolvers thin and route through application use cases;
- enforce query depth/complexity, authorization, batching, and pagination;
- avoid exposing persistence models as the schema;
- test schema compatibility and resolver authorization separately.

Do not add a GraphQL runtime, schema, or MCP server to a project that does not
use GraphQL. See `references/graphql-patterns.md` for the concrete adoption
pattern (codegen, thin resolvers, N+1/complexity/authorization, and the
GraphQL-equivalent lint/breaking-change tooling) once one genuinely does.

## Guardrails

- Never put secrets, internal stack traces, or sensitive identifiers in examples.
- Avoid silent breaking changes: removed fields, tightened validation, changed
  nullability, reordered semantics, or reused status codes.
- Prefer additive evolution; version only when compatibility cannot be preserved.
- Keep OpenAPI/GraphQL transport concerns out of core and application layers.

## Standard error responses

| Status | When | Scope |
| --- | --- | --- |
| 400 | Malformed request the framework can't otherwise classify | Rare; prefer 422 |
| 401 | Missing/invalid credentials (once auth exists) | Global, once auth is added |
| 403 | Authenticated but not authorized | Per-route |
| 404 | Resource lookup failed (a named `*NotFoundError(DomainError)` from `ddd`'s `assets/domain_exceptions.py.template` — never a bare stdlib `LookupError` catch) | Per-route (only lookup routes) |
| 409 | Conflicting state (e.g. duplicate create) | Per-route |
| 413 | Request body exceeds the size limit (`RequestBodyLimitMiddleware`) | Global — any route can receive an oversized body |
| 422 | Request/response schema validation failure (`RequestValidationError`, `ValidationError`, bare `ValueError`) | Global |
| 429 | Rate limit exceeded (`RateLimitExceeded`) | Global |
| 500 | Unhandled exception (catch-all) | Global |
| 502 | An external client port returned an unusable result (one distinctly-named `*Error(DomainError)` per client port/failure mode — never one generic type reused across unrelated ports) | Per-route — only routes that call an external client (LLM, OCR, ...) |
| 503 | Persistence/dependency temporarily unavailable (`PersistenceUnavailableError`) | Global if every route can touch persistence |

400/401/403/409 have no dedicated constant in
`assets/error_responses.py.template` until a project actually has a route
that can produce them (auth, conflict detection) — add one only once a real
call site needs it; do not pre-build unused response constants. 422 is the
default validation status for both FastAPI's own `RequestValidationError`
and the `backend-structure` skill's `exception_handlers.py.template` mapping
of a bare domain `ValueError`, so a single schema documents both causes.

## Templates and references

- [`references/versioning-strategies.md`](references/versioning-strategies.md)
  — URI/header/media-type trade-offs, deprecation headers, and a
  breaking-vs-non-breaking quick reference.
- [`references/graphql-patterns.md`](references/graphql-patterns.md) — schema
  codegen, thin resolvers, N+1/complexity/authorization, and GraphQL-equivalent
  lint/breaking-change tooling for the day GraphQL is actually adopted.
- [`assets/route.py.template`](assets/route.py.template) — a single-resource
  endpoint module skeleton with typed request/response schemas.
- [`assets/dto_model.py.template`](assets/dto_model.py.template) — the shared
  configured Pydantic base (mutable/frozen), `Annotated` `Field` metadata, and
  cross-field `model_validator` pattern for request/response DTOs.
- [`assets/error_responses.py.template`](assets/error_responses.py.template) —
  the documented error envelope, OpenAPI example builders, and a reusable
  `STANDARD_ERROR_RESPONSES` map (404/413/422/429/500/502/503) for the
  `responses=` kwarg — see the "Standard error responses" table above for
  which are global vs per-route. Pair with the `backend-structure` skill's
  `assets/exception_handlers.py.template`, which produces this envelope at
  runtime.
