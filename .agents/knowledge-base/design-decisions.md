# Design decisions

## Local-first SQLite

SQLite is the local desktop/test persistence default. It is not shared storage
for horizontally scaled Azure Container Apps; production persistence requires a
separate deliberate database decision.

## GraphQL is selective

GraphQL is retained where it teaches or provides transport value—especially the
real-time transcript subscription. Operational health remains REST because
platform probes need fixed, cacheable HTTP endpoints.

## Multi-runtime agent configuration

Skills are byte-identical across `.github`, `.claude`, and `.agents`. Provider
agents and instruction scopes may differ where runtime syntax or the monorepo
requires it. `PROJECT.md` owns project facts; portable skills contain no Ekko
identity tokens.

## Lean active MCP inventory

Only Context7 and GitNexus are active. Storybook and Figma remain opt-in because
they require a local service or external authorization.
