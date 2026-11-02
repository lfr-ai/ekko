# GraphQL adoption patterns

Reference material for the day a consumer need actually justifies GraphQL (see
`SKILL.md`'s "REST and GraphQL" guardrail — do not adopt this speculatively).
REST stays the default; use this once a verified client-directed, graph-shaped
read requirement exists (for example a UI composing many nested, caller-chosen
relations that would otherwise need several round trips or bespoke aggregation
endpoints).

## Schema-first workflow

- Treat the SDL (schema definition language) as the contract, the same way an
  OpenAPI document is the contract for REST. Keep it generated from code
  (code-first) or hand-authored and enforced by resolver types (schema-first) —
  pick one direction per project, never both.
- Wire client codegen through a `.graphqlrc.yml` pointing at the live
  introspection endpoint (or a committed SDL file) plus the operation
  documents that need typed generated clients, for example:

  ```yaml
  projects:
    frontend:
      schema:
        - http://localhost:8000/graphql
      documents:
        - frontend/src/infrastructure/graphql/operations/**/*.graphql
  ```

- Generate typed operations with `@graphql-codegen/cli` (client preset) rather
  than hand-writing query/response types on the frontend.

## Server implementation (Python / FastAPI stack)

- Use Strawberry (`strawberry.fastapi.GraphQLRouter`) — it is code-first,
  type-hint driven, and mounts onto the existing FastAPI app factory like any
  other router from the `backend-structure` skill.
- **Thin resolvers only.** A resolver calls the same application-layer use
  case or service a REST route would call; it never re-implements a query,
  aggregation, or authorization rule that already exists behind a REST
  endpoint. Two transports, one application layer.
- **N+1 avoidance.** Batch related lookups with `strawberry.dataloader.DataLoader`
  keyed by ID; never issue one repository call per resolved field inside a
  list comprehension.
- **Depth/complexity limiting.** Enforce a maximum query depth and alias count
  as schema-level extensions (Strawberry's `QueryDepthLimiter` /
  `MaxAliasesLimiter`, or an equivalent validation rule) — never rely on
  resolver-level checks, which run too late to stop an expensive query plan.
- **Authorization.** Apply field- and type-level permission classes
  (`strawberry.permission.BasePermission`) that call the same authorization
  port/service the REST layer uses. Never duplicate the policy in the
  resolver.
- **Pagination.** Default to Relay-style cursor connections (`edges` / `node`
  / `pageInfo`) — it is the community-standard shape or generated clients
  already expect it.

## Linting and schema-compatibility checks

Redocly does not parse GraphQL SDL — it is an OpenAPI/AsyncAPI JSON-Schema
linter. The GraphQL-equivalent tooling:

- **Schema linting** — `@graphql-eslint/eslint-plugin` (naming conventions,
  deprecated-field usage, description requirements) for SDL/resolver files.
- **Breaking-change detection** — `@graphql-inspector/cli diff` comparing the
  current schema against the previous release's committed SDL or a live
  endpoint; this is the GraphQL analog of comparing OpenAPI documents across
  releases (`SKILL.md` workflow step 7).

Wire whichever of these a project adopts as its own on-demand task; keep its
exact task name in the project facts. Do not make these pre-commit hooks because
they need network/`bunx` access.

## Testing

- Resolver unit tests call the resolver function directly against the same
  application-layer fakes/mocks used for REST route tests.
- Add schema-level tests that execute real GraphQL documents against the test
  schema to catch resolver-wiring regressions a unit test alone would miss
  (mirrors REST's route-level contract tests in workflow step 5).

## Related

- `SKILL.md` — the REST/GraphQL guardrail this file elaborates on.
- `backend-structure` skill — app factory and router-mounting conventions a
  `GraphQLRouter` follows identically to a REST `APIRouter`.
