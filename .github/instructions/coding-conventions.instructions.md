---
description: Python coding conventions and type safety standards
applyTo: "**/*.py"
---

## Python Conventions

- Use full type hints and Google-style docstrings.
- **Imports — qualified vs direct** (one style per package, applied everywhere;
  never import the same package both ways; applies to classes *and* functions):
  - **Direct** (`from x import Y`): `typing`, `collections.abc`,
    `typing_extensions`, `dataclasses`, `enum`, `pathlib` (`Path`), `datetime`,
    `uuid`, `contextlib`, `decimal`; distinctive framework symbols
    (`pydantic.BaseModel`, `fastapi.FastAPI`, `sqlalchemy`, `langgraph`); all
    first-party `myapp.*` symbols.
  - **Qualified** (`import x` → `x.Y`): stdlib utility modules with generic
    member names (`logging`, `os`, `sys`, `json`, `re`, `asyncio`, `hashlib`,
    `html`, `shutil`, `inspect`, `argparse`); namespace-heavy third-party
    (`httpx`, `litellm`, `fitz`, `duckdb`); aliased scientific libs
    (`numpy as np`, `polars as pl`).
  - Enforced by ruff `flake8-import-conventions` (`ICN`): `banned-from` +
    `aliases`. Basis: Google Style Guide §2.2 for the qualified set; PEP 8
    pragmatism for the universal direct set.
  - **First-party module-object exception**: tests/tools that need a module
    object for monkeypatching, reloading, or package-surface assertions MAY use
    `import myapp.main as main_module`. This imports a module, not an individual
    symbol, and does not permit mixing symbol-import styles.
- Package `__init__.py` files carry a single-line module docstring. Namespace
  packages are docstring-only (no imports, no `__all__`). Re-export hubs add
  explicit `from … import …` plus an `__all__` listing exactly the re-exported
  (and any locally-defined) public names — a bijection with the imports — kept
  isort-sorted. Re-export via `from module import Name` + `__all__`, never
  redundant aliases. Machine-enforced by ruff `RUF022` and `F401`.
- Never use 'Any' in annotations. Use precise unions/protocols, and use 'object' as fallback when unconstrained values are required.
- Never use `typing.cast`/`cast(...)`. Refactor code so inferred/static types are correct without casts.
- Do not use string-literal forward references in annotations (for example `"AppConfig"`).
  When forward references are needed, use `from __future__ import annotations`.
- For dataclasses, always use keyword-only initialization:
  - Use `kw_only=True` for all dataclasses.
  - Use `frozen=True, kw_only=True, slots=True` for immutable value-like objects.
  - Mutable entities/services may omit `frozen` (the default is `False`) but still use `kw_only=True`.
  - Prefer `slots=True` for mutable dataclasses when compatible (no dynamic attribute requirements or incompatible inheritance constraints).
- Prefer `@property` for computed attributes. `@cached_property` requires a `__dict__`
  and is incompatible with `slots=True`; reserve it (on non-slotted classes) for
  expensive, stable computations or lazily-memoized singletons such as `Container`.
- Remove dead code promptly (unused private/public methods, constants, and imports).
- Do not add backward-compatibility shims, alias modules, or deprecated wrappers.
  Prefer coordinated call-site updates and remove deprecated paths in the same change-set.
- All docstrings with `Args`, `Returns`, `Yields`, or `Raises` sections MUST include type annotations for each parameter and return value.
- Prefer explicit, small, composable functions.
- Keep runtime behavior idempotent where startup hooks are involved.
- Use structured logging.
- Keep environment/database behavior deterministic across environments.
- Reserve `Final` for public module constants only. Do not annotate internal
  (underscore-prefixed) variables with `Final`.
- Internal constants (underscore-prefixed module-level names) must not be
  type-annotated at all.
- Prefix private/internal module-level constants, helper functions, and non-exported
  names with `_`.
- For stdlib `logging`, use `import logging` and module-qualified members in all
  class/function signatures and call sites (for example `logging.LogRecord`,
  `logging.Filter`, `logging.getLogger`). Do not use
  `from logging import <symbol>` or `from logging.handlers import <HandlerClass>`.
- In docstring 'Raises' sections, only list exceptions that the function itself raises
  directly. Do not propagate 'Raises' from called sub-functions.
- Use triple-quoted docstrings (`"""..."""`) for all docstrings, including
  single-line summaries.
  - Good: `"""Case identifier."""`
  - Bad: `"Case identifier."`
- Write the acronym `DTO`/`DTOs` in prose, docstrings, and docs. The expanded
  form "data transfer objects" appears exactly once, in the
  `myapp.application.dtos` package docstring. Do not describe DTO classes as
  "Pydantic models", "schemas", or "payload models".
  - Good: `"""Case lifecycle DTOs."""`
  - Bad: `"""Case lifecycle data transfer objects."""`
- Never start a docstring summary line with any of these words:
  "Return", "Returns", "Response", "Request", "Payload".
  Use a descriptive noun-phrase or imperative verb instead.
  - Good: `"""Case identifier."""` or `"""Provide helper for inserting rows."""`
  - Good: `"""Successful case creation payload."""` or `"""New case creation data."""`
  - Bad: `"""Return case identifier."""` or `"""Returns the case ID."""`
  - Bad: `"""Response returned after case creation."""` or `"""Response for upload."""`
  - Bad: `"""Request payload for creating a customer."""` or `"""Payload for\u2026"""`
- Property docstrings use simple noun-phrase one-liners describing what the
  property represents. Do not add `Returns:` sections to property docstrings.
  - Good: `"""Unique case identifier."""`
  - Bad: `"""Return case identifier.\n\n    Returns:\n        UUID: ...\n    """`
- Route handler functions use simple one-liner docstrings when the route decorator
  already provides a `description=` parameter with full API documentation.
  Do not duplicate endpoint docs in the docstring.
  - Good: `"""Create a case record."""`
  - Bad: Multi-line docstrings restating the decorator description
- `__init__` methods must NEVER annotate a return type. The implicit `None`
  return is universally understood and the annotation adds noise.
  - Good: `def __init__(self, *, name: str):`
  - Bad: `def __init__(self, *, name: str) -> None:`

## Custom Types (Domain Scalars)

Pick the lightest tier that fits; define shared types in `core/types.py` (or a
layer-local `types.py`). Each tier has a fixed trigger, so classification is
never a judgment call:

1. **Validated value object** — the value carries an enforceable invariant that
   must hold at a trust boundary (config, request, persistence). Validate in
   `__new__` (scalar subclass) or `__post_init__` (compound): `MaxTokens` (> 0,
   ≤ 1_000_000), `Temperature` ([0, 2]), `Confidence` ([0, 1]), `CPR`. Add
   Pydantic hooks only when the type is a model field (`Confidence`).
2. **Structural alias (`type`)** — names a recurring compound shape
   (dict/tuple/callable) with no scalar invariant: `EmbeddingComponents`,
  `JSONDict`, the `Rectangle` NamedTuple.
3. **Decoupling alias (`type`)** — a core stand-in for a value whose
   concrete type is an enum owned by an outer layer that core must not import:
   `ModelDeploymentName` (a `ChatModel`/`EmbeddingModel` value), `StrategyName`
   (a `RagStrategy` value). Application/infrastructure use the concrete enum.
4. **`NewType`** — an opaque scalar identifier kept distinct for the checker,
   with no arithmetic and no runtime invariant; requires explicit wrapping
   `X(value)`. Use only where distinctness prevents real bugs.
5. **Bare primitive** — a local, measured, or computed value with no boundary
   invariant: counts used in arithmetic (`int`), free-form text (`str`), one-off
   collections (`tuple[float, float]`). When such a value lives inside a value
   object, that object validates it (`RetrievalDiagnostics` rejects negative
   counts).

Guiding principle: a constrained **input** you set (a token limit) is a value
object (`MaxTokens`); a measured **output** you receive (a token count) is a
primitive validated by its container. That distinction — not the shared `int` —
is why `MaxTokens` is a value object while token/chunk counts are not.

Concrete rule for retrieval flows:
- `RetrievalQuery.max_context_tokens` is a constrained input budget -> `MaxTokens`.
- `RetrievalDiagnostics.prompt_tokens` / `retrieved_chunks` are measured outputs
  used in arithmetic -> bare `int` values validated by `RetrievalDiagnostics`.
- `top_k`, `chunk_size`, `chunk_overlap` are internal knobs sourced only from
  validated module constants (`RAG_TOP_K`, `RAG_CHUNK_SIZE`, `RAG_CHUNK_OVERLAP`
  as `Final[int]`); they never cross a trust boundary and stay bare `int`, not
  value objects.

Do not create a scalar type alias purely for documentation (e.g. `PromptContent
= str`): it adds neither safety nor distinctness. Use a primitive with a
descriptive parameter name, or promote to `NewType`/a value object when the tier
triggers apply.

## Annotated-first Metadata (FastAPI + Pydantic)

- Prefer `typing.Annotated` for FastAPI parameter/dependency metadata:
  - `Annotated[..., Query(...)]`, `Path`, `Body`, `Header`, `Cookie`, `Form`,
    `File`, and `Depends`.
- Prefer `Annotated[..., Field(...)]` for Pydantic constraints and schema metadata
  when no constructor-shaping behavior is required.
- Prefer assignment form (`field: Type = Field(...)`) when using
  `default`, `default_factory`, or `alias`, because static type checkers use those
  to synthesize model constructor signatures.
- Avoid legacy FastAPI default-style declarations such as
  `param: str = Query(...)` in new code.

## Configuration Layer & `from_config`

Two conventions govern application configuration (the config package):

- **`*Settings` vs `*Config` naming.** A `*Settings` class is an
  environment-sourced *facet*: a `pydantic_settings.BaseSettings` subclass that
  owns one cohesive group of prefixed environment fields (e.g. `MYAPP_*`) and
  composes into the aggregate — `DatabaseSettings`, `ServerSettings`, … under
  `config/settings/`. A `*Config` is a *complete, assembled configuration*: the
  aggregate `AppConfig` and each environment subclass (`LocalConfig`,
  `DevelopmentConfig`, `ProductionConfig`), **and** a consumer's structural view
  of that config (below). In short: `Settings` owns/sources fields; `Config` is
  the assembled object or a view of it.
- **`from_config` + consumer-owned config `Protocol`.** A component built from
  application configuration exposes `from_config(cls, config: _XConfig) -> Self`,
  where `_XConfig` is a **private** structural `typing.Protocol` declared in the
  same module listing only the fields the component reads:

  ```python
  class _EmailClientConfig(Protocol):
      smtp_host: str
      smtp_password: SecretStr

  class EmailClient(EmailClientPort):
      @classmethod
      def from_config(cls, config: _EmailClientConfig) -> Self:
          return cls(host=config.smtp_host, password=config.smtp_password)
  ```

  The component **never imports** the aggregate `AppConfig` or a config facet;
  `AppConfig` satisfies `_XConfig` *structurally* (PEP 544 — static type checkers
  recognize protocol implementations even when the protocol is not imported),
  keeping infrastructure decoupled from the config layer (dependency inversion).
  Name the Protocol `_<Component>Config` (a view of the config object) — never
  `_<…>Settings`, which is reserved for the field-owning facets. Keep each
  Protocol compact; PEP 544 recommends small, focused protocols.

## Cognitive Load

See `cognitive-load.instructions.md` for complete guidelines. Key rules that
apply to all Python code:

- Extract complex boolean expressions into named intermediate variables.
- Prefer early returns over deeply nested conditionals.
- Prefer deep modules (simple interface, complex implementation) over many
  shallow wrappers.
- Keep related code together — avoid scattering tightly-coupled logic across
  multiple tiny functions that must be read together.
