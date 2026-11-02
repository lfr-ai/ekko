---
name: configuration
description: Add or change an environment variable or application configuration value the right way — through a typed settings facet, the env templates, and the from_config protocol. Use when introducing, renaming, or documenting configuration, secrets, or environment variables.
---

# Configuration & environment variables

Configuration is assembled from **`*Settings` facets** — each owns one cohesive
group of fields (the project's env prefix and facet names live in `PROJECT.md`).
Every facet composes into the aggregate `AppConfig` the same way: as a **nested
field**, never via multiple inheritance. This applies uniformly whether the
concern is intrinsic to the app (`configs/settings/*.py`, e.g. database, server,
model deployments), whether its parent attribute already carries the context
(`paths.root`, `paths.logs`), or whether it is a vendor/provider concern
(`configs/settings/integrations/*.py`, e.g. an OAuth2 client or a model
provider). A facet subclasses `NestedSettings` (`pydantic.BaseModel`, never
`pydantic_settings.BaseSettings` directly) and the aggregate composes it as a
typed field. Only the aggregate `AppConfig` itself subclasses
`pydantic_settings.BaseSettings` (via the shared `ConfiguredSettings` base,
which sets `env_prefix`, `env_nested_delimiter="__"`, and
`nested_model_default_partial_update=True`) — there is no other use for
multiple inheritance of `BaseSettings` in this pattern; pydantic-settings'
own docs demonstrate nested `BaseModel` sub-models, not composing multiple
`BaseSettings` subclasses, as the way to group settings. `AppConfig` has one
`@final` subclass per environment (`configs/environments/*.py`: `LocalConfig`,
`DevelopmentConfig`, `TestConfig`, `StagingConfig`, `ProductionConfig`).
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

Since every facet is nested, `_XConfig` almost always layers **two** Protocols:
an outer one exposing the nested facet as a property returning an inner
Protocol that lists only the leaf fields read from it — mirroring the real
facet's own nesting instead of flattening it away:

```python
class _DatabaseConfig(Protocol):
    @property
    def url(self) -> str: ...


class _RepositoryConfig(Protocol):
    @property
    def database(self) -> _DatabaseConfig: ...
```

A component then reads `config.database.url`, `config.chat_provider.api_key`,
etc. — never a flattened `config.database_url`. See
`infrastructure/persistence/repositories/_base.py` (`_DatabaseConfig` +
`_RepositoryConfig`) and `infrastructure/clients/chat.py` (`_ChatProviderConfig`
+ `_ChatConfig`) for the two concrete shapes this takes.

## When `from_config` applies (and when it doesn't)

`from_config` is for a component that reads **external configuration values**
(a connection string, an API key, an endpoint URL, a deployment name) to build
its own state. It is **not** a mandatory interface every port/adapter must
implement — do not add a base class or Protocol method to force it; that would
make every stateless or purely-composed adapter carry a vacuous `from_config`
that ignores its `config` argument, which is worse than not having one. Decide
per adapter:

- **Needs `from_config`**: the adapter's `__init__` params are themselves
  sourced from config (API keys, base URLs, model providers) — e.g. a chat
  client built from Azure OpenAI settings.
- **No config, `__init__` only**: a stateless or in-memory adapter with a
  zero-arg constructor (a pure-function wrapper, an in-memory store). Adding
  `from_config` here would just be `cls()`, discarding its argument — skip it
  and construct the adapter directly in the composition root.
- **Composed from other ports**: an adapter whose dependencies are *other
  already-built ports* (plus maybe one config-derived scalar) is wired
  directly in the composition root from those already-resolved ports, not
  reconstructed from raw config — the container already owns that
  composition; re-deriving it inside `from_config` would duplicate the
  container's wiring logic and hide it from the one place that should own it.

This mirrors the repo's Protocol-first, structural-typing design (PEP 544):
ports are `Protocol`s precisely so nothing is forced through a shared
nominal base class. A short one-line docstring/comment on an adapter that
deliberately has no `from_config` ("stateless, no config needed") is enough
to make the decision self-documenting — no enforcement script should require
every adapter to have one.

### Enforcing it where it does apply: `FromConfigMixin`

For the adapters that DO need `from_config`, forgetting to implement it should
fail loudly, not just fail an on-demand lint script. Mix in
`infrastructure/_from_config.py`'s `FromConfigMixin[ConfigT]` (an `abc.ABC`,
parameterized with the adapter's own private `_XConfig` Protocol) alongside
the adapter's Port:

```python
class ChatClient(ChatClientPort, FromConfigMixin[_ChatConfig]):
    @classmethod
    @override
    def from_config(cls, config: _ChatConfig, /) -> Self: ...
```

This lives entirely in Infrastructure (never Core) precisely because the
`_XConfig` Protocol's fields are often typed with library types (e.g.
`pydantic.SecretStr`) that Core's Hard Rule 18 stdlib-only boundary forbids -
putting the abstract `from_config` requirement on the Core `Protocol` port
itself is not possible without violating that boundary. Since
`FromConfigMixin` is an `abc.ABC`, Python refuses to instantiate a subclass
that omits `from_config` (`TypeError: Can't instantiate abstract class ...`)
- a real runtime guarantee, not a lint suggestion. Do not mix it into a
stateless or ports-composed adapter (see the criteria above) - only where
`from_config` genuinely applies.

Repositories already get an equivalent guarantee a different way: every
concrete repository inherits `RepositoryBase`'s single, shared, non-abstract
`from_config` wholesale (they never redefine it per repository), so there is
no per-repository chance to omit it - no separate mixin needed there.

## Nested facet naming and shape

Every facet's parent attribute already carries its concern's context, so drop
any field name that repeats it — this applies just as much to an intrinsic app
concern as to a filesystem path or a vendor concern: use `database.host`, not
`database.postgresql_host`; `server.port`, not `server.uvicorn_port`; `paths.logs`,
not `paths.logs_dir_path`; `chat_provider.api_key`, not
`chat_provider.chat_provider_api_key`. Reserve a qualifying prefix/suffix only
when the bare noun would be ambiguous in its immediate context (`ssl_keyfile`
next to a plain `port` disambiguates which credential; `_path` marks a specific
file rather than a directory).

Only the target folder distinguishes an intrinsic concern (bare
`configs/settings/*.py`, e.g. database, server, model deployments) from a
vendor/provider one (`configs/settings/integrations/*.py`, e.g. an OAuth2
client, an AI model provider) — the composition shape is identical (see the
intro): one `NestedSettings` field, no `env_prefix` of its own, sourced from
`<PREFIX>_<FACET>__<FIELD>`. One template
([`assets/nested_settings_facet.py.template`](assets/nested_settings_facet.py.template))
covers both.

When a nested facet has a default instance and individual fields may be
overridden from env vars, set `nested_model_default_partial_update=True` on the
aggregate `ConfiguredSettings` base so `<PREFIX>_<FACET>__<FIELD>` updates only
that field and preserves the nested model's other defaults.

## Per-environment configuration

Each environment subclass in `configs/environments/` overrides **only** the
fields that genuinely differ for that target (`model_config.env_file`, plus any
field whose value diverges from the shared default on `BaseAppConfig`/the
facets it composes). Never re-declare a field with the exact value it already
inherits — a redundant override reads as a real per-environment decision when
it is not, and the two facts drift silently once someone changes the shared
default and forgets the copy. Before adding an override, check whether the
inherited default already matches; if it does, delete the line instead.

## Deployment-target duality (on-prem + containers)

`Environment` resolves from an explicit env-var override first (the project's
prefix + `ENVIRONMENT`, e.g. `<PREFIX>_ENVIRONMENT`), falling back to a fixed
on-prem hostname map (`configs/runtime.py`) — never hostname-only. On-prem
Windows Servers have stable, pre-known hostnames; a container (Docker, Azure
Container Apps) does not, so it must declare its stage explicitly via the
override variable. Reuse this pattern instead of adding a fourth `Environment`
member per hosting target — the same `DevelopmentConfig`/`ProductionConfig`
classes serve both, only the resolution path differs.

A default that only holds on-prem (e.g. a local TLS cert path — ingress
terminates TLS for a Container App, so the container must not also try to load
one) is nulled per target via `env_parse_none_str="null"`
(`configs/settings/_shared.py`): set the field's env var to the literal string
`null` in the container's env vars rather than adding an on-prem-only field to
a facet.

## Before finishing

- The variable appears in `.env.example` and every environment that needs it.
- No secret or machine-specific value is committed.
- Naming holds: `*Settings` sources fields; `*Config` is the assembled object or a
  structural view of it.
- A field with an on-prem-only default is nulled for the container/cloud target
  via its deployment's env vars, not hardcoded around in a new facet.
- Every concern — intrinsic or vendor/provider — is a `NestedSettings` field on
  the aggregate, never a top-level inherited facet.
- No environment subclass re-declares a field value identical to what it
  already inherits.
- Every `pydantic.BaseModel`/`BaseSettings` subclass sets `extra="forbid"`
  (directly or via a shared base) — never left at the library default.

## Templates

- [`assets/nested_settings_facet.py.template`](assets/nested_settings_facet.py.template)
  — one cohesive `*Settings` facet (intrinsic or vendor/provider) with a
  `SecretStr` field and a `cached_property`, composed as a nested field.
- [`assets/from_config_component.py.template`](assets/from_config_component.py.template)
  — the private `_XConfig` Protocol + `from_config` classmethod pattern, layered
  to mirror a nested facet.
- [`assets/environment_config.py.template`](assets/environment_config.py.template)
  — an `@final` per-environment `*Config` subclass that overrides only genuine
  deltas.

## Enforcement

- [`scripts/check_from_config_pattern.py`](scripts/check_from_config_pattern.py)
  — flags a `from_config` classmethod whose config parameter is a public type
  (the concrete aggregate config) instead of a private, locally-defined
  `_XConfig` Protocol. Neither ruff nor ty know this project-specific
  convention. Read-only; run:
  `uv run python scripts/check_from_config_pattern.py src/<pkg>`.
