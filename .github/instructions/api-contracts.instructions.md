---
description: OpenAPI, Redocly, and GraphQL contract-file conventions
applyTo: "**/openapi*.json, **/openapi*.yaml, **/openapi*.yml, **/redocly.yaml, **/redocly.yml, **/*.graphql, **/*.gql"
---

# API contract files

- Treat OpenAPI and GraphQL schemas as compatibility boundaries; prefer additive
  evolution and document intentional removals, nullability changes, and renamed
  fields before release.
- Keep generated OpenAPI output (`openapi.json`) generated — change
  `tools/generate_openapi.py` and route/schema definitions rather than
  hand-editing the artifact.
- Redocly config (`redocly.yaml`) owns structural OpenAPI linting. Pin rules,
  keep exceptions narrow and explained, and run the CI contract-lint job after
  changing either config or schema.
- GraphQL operations use stable names and generated result/variable types.
  Never interpolate values into operation text; send variables separately.
- Follow the `api-contracts` skill for the design, generation, lint, and rollout
  workflow; do not add GraphQL to a REST route speculatively — this repo's
  GraphQL surface stays a single minimal `promptCatalog` query by design.
