---
name: configuration
description: Add or change an environment variable or application configuration value the right way — through a typed settings facet, the env templates, and the from_config protocol. Use when introducing, renaming, or documenting configuration, secrets, or environment variables.
---

# Configuration & environment variables

Configuration is assembled from **`*Settings` facets** — each a
`pydantic_settings.BaseSettings` subclass owning one cohesive group of prefixed
environment fields (the project's env prefix and facet names live in
`PROJECT.md`). Facets compose into the aggregate `AppConfig`, which has one
subclass per environment (`LocalConfig`, `DevelopmentConfig`, `ProductionConfig`).
Components never read the environment directly; they receive a config object.

## Add or change a variable

1. Add a typed field to the **facet** that owns its concern; create a new facet
   only for a genuinely new concern. Give it a sane default unless it is a
   required secret.
2. Update **`.env.example`** — the single source of truth for supported
   variables — plus any per-environment template that needs an override.
3. Type it by tier: a value crossing a trust boundary with an invariant (a bound,
   a format) is a value object; a measured value or a knob sourced from a
   validated module constant stays a primitive.
4. Secrets are `SecretStr`, sourced from the environment only — never a literal in
   code, a default, or a committed template value.
5. Update `PROJECT.md` only when a project-level fact changes (a new prefix or a
   new required-variable class), not for every field.

## Consuming config: `from_config`

A component built from configuration exposes
`from_config(cls, config: _XConfig) -> Self`, where `_XConfig` is a **private**
structural `typing.Protocol` in the same module listing only the fields it reads.
It never imports the aggregate config; the config satisfies `_XConfig`
structurally (PEP 544), keeping the component decoupled from the config layer.
Name the view `_<Component>Config` — never `_<…>Settings`, which is reserved for
the field-owning facets.

## Before finishing

- The variable appears in `.env.example` and every environment that needs it.
- No secret or machine-specific value is committed.
- Naming holds: `*Settings` sources fields; `*Config` is the assembled object or a
  structural view of it.
