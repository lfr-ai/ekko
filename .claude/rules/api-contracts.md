---
paths:
  - "**/openapi*.json"
  - "**/openapi*.yaml"
  - "**/openapi*.yml"
  - "**/redocly.yaml"
  - "**/redocly.yml"
  - "**/*.graphql"
  - "**/*.gql"
---

# API contract files

- Treat OpenAPI and GraphQL schemas as compatibility boundaries; prefer additive
  evolution and document intentional removals, nullability changes, and renamed
  fields before release.
- Keep generated OpenAPI output generated. Change its typed source models and
  route metadata rather than hand-editing the artifact.
- Redocly config owns structural OpenAPI linting and bundling. Pin rules and
  plugins, keep exceptions narrow and explained, and run the repository-owned
  contract task after changing either config or schema.
- GraphQL operations use stable names, bounded pagination, fragments for shared
  selections, and generated result/variable types. Never interpolate values into
  operation text; send variables separately.
- GraphQL schema changes require compatibility checks plus resolver authorization
  tests. Keep persistence types and secrets out of both schema descriptions and
  examples.
- Follow the `api-contracts` skill for the design, generation, lint, and rollout
  workflow; do not add GraphQL to a REST project speculatively.
