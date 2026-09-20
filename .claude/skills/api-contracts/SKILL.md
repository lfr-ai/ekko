---
name: api-contracts
description: Design, evolve, and verify HTTP API contracts for REST/FastAPI/OpenAPI, Swagger UI, Postman, or GraphQL. Use when adding endpoints, changing request/response schemas, versioning an API, or reviewing contract compatibility.
---

# API contracts

Treat the published contract as a compatibility boundary. Keep transport code in
presentation and business rules behind application/core ports.

## Workflow

1. Identify consumers, authentication, idempotency, pagination, rate limits, and
   compatibility constraints before choosing an endpoint shape.
2. Model stable resource nouns and HTTP semantics: methods, status codes,
   headers, cache behavior, and one documented error envelope.
3. Define typed request/response schemas at the boundary. Do not expose ORM or
   domain entities directly.
4. Generate OpenAPI from the application (`tools/generate_openapi.py`) and
   inspect operation IDs, security schemes, examples, nullability, formats, and
   reusable components. Redocly (`redocly.yaml`) lints the generated
   `openapi.json` for a structural pass — missing tags/descriptions, invalid
   examples, unused components — that behavioral contract tests do not check;
   this runs as a CI gate (`.github/workflows/ci.yml`).
5. Add contract tests for success, validation, authorization, not-found,
   conflict, and unexpected-failure behavior.
6. Update Postman collections (`postman/`) only when they are an owned contract
   source; avoid hand-maintained duplicates of generated OpenAPI.
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
  declarations of the same shape can drift out of sync with each other, which
  a single return-type annotation cannot. Reserve the `response_model=` kwarg
  for the rare case where the wire response genuinely differs from the return
  type.
- Keep `/docs`, `/redoc`, and `/openapi.json` configurable. Public production
  exposure is a security decision, not a default.
- Give operations stable IDs if generated clients depend on them.
- Validate examples and security requirements; a rendered Swagger page is not a
  substitute for contract tests.
- Hide non-`/api` infrastructure routes (health checks, metrics, and similar
  browser/deploy-tooling endpoints, as opposed to business routes) from the
  schema with `include_in_schema=False`, and state that convention once in the
  module's docstring.
- For a status code that carries no body (204, 304), declare `status_code=`
  once, on the decorator, and return `None` (or omit the return) instead of
  also constructing a `Response(status_code=204)`.

## REST and GraphQL

Prefer REST for resource-oriented operations unless GraphQL solves a verified
consumer need such as client-directed graph-shaped reads. This repo's GraphQL
surface (`presentation/graphql/`) is deliberately minimal — ONE read-only
`promptCatalog` query, no mutations/subscriptions — because REST already
covers the command/streaming surface; do not grow it beyond a genuine need. If
GraphQL is present:

- keep resolvers thin and route through application use cases;
- enforce query depth/complexity, authorization, batching, and pagination as
  the schema grows;
- avoid exposing persistence models as the schema;
- test schema compatibility and resolver authorization separately
  (`tests/unit/presentation/test_graphql_schema.py`).

Do not add a GraphQL runtime, schema, or MCP server to a project that does not
use GraphQL.

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
| 404 | Resource lookup failed (a named `*NotFoundError` from `core/exceptions`, never a bare stdlib `LookupError` catch) | Per-route (only lookup routes) |
| 409 | Conflicting state (e.g. duplicate create) | Per-route |
| 413 | Request body exceeds the size limit | Global — any route can receive an oversized body |
| 422 | Request/response schema validation failure (`RequestValidationError`, `ValidationError`, bare `ValueError`) | Global |
| 429 | Rate limit exceeded (slowapi) | Global |
| 500 | Unhandled exception (catch-all) | Global |
| 502 | An external client port returned an unusable result (one distinctly-named error per client port/failure mode) | Per-route — only routes that call an external client (LLM, STT, ...) |
| 503 | Persistence/dependency temporarily unavailable | Global if every route can touch persistence |
