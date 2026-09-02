---
paths:
  - "**/*.py"
---

# Python Conventions

## Python Version
- Target: Python 3.13+
- Use modern syntax: `X | Y` unions and `match` statements when appropriate.
  Use the PEP 695 `type` statement for explicit type-checker aliases (`type X = ...`)
  and PEP 695 generics (`class C[T]`, `def f[T]()`). Reserve `NewType` for opaque
  identifiers, and a plain module-level `Annotated` assignment for runtime FastAPI
  dependency markers (the value is introspected at request time, so it is not a
  `type` alias).

## Imports

### Qualified vs Direct
Pick one style **per package** and apply it **everywhere** — never import the
same package both ways. The choice applies to **classes *and* functions**.

**Direct** (`from x import Y`) — bind the symbol. Use for:
- Typing/ABCs: `typing`, `collections.abc`, `typing_extensions`
- Standard structural types: `dataclasses`, `enum`, `pathlib` (`Path`),
  `datetime` (`datetime`, `date`), `uuid` (`UUID`), `contextlib`, `decimal`
- Distinctive framework symbols: `pydantic` (`BaseModel`, `Field`),
  `fastapi` (`FastAPI`, `APIRouter`), `sqlalchemy`, `langgraph`
- All first-party `myapp.*` symbols

**Qualified** (`import x` → `x.Y`) — keep the namespace. Use for:
- Stdlib utility modules with generic member names: `logging`
  (`logging.Filter`, `logging.getLogger`), `os`, `sys`, `json`, `re`,
  `asyncio`, `hashlib`, `html`, `shutil`, `inspect`, `argparse`
- Namespace-heavy third-party: `httpx` (`httpx.Response`), `litellm`, `fitz`,
  `duckdb`; aliased scientific libs `numpy as np`, `polars as pl`

### Rules
1. **One style per package, everywhere.** Mixing (`logging.Filter` in one module,
   `from logging import Filter` in another) is forbidden.
2. **Classes and functions alike.** `json.loads`, `logging.getLogger`,
   `httpx.get` stay qualified just like `logging.Filter`, `httpx.Response`.
3. **No direct logging imports.** Use `import logging` + `logging.<Symbol>` and
    `logging.handlers.<HandlerClass>` instead of `from logging import ...` and
    `from logging.handlers import ...`.
4. **Qualify generic names.** If the bare symbol (`Filter`, `load`, `get`,
   `Response`) would be ambiguous at the call site, keep the namespace.
5. **Only conventional aliases.** `np`, `pl` — do not invent new aliases.
6. **First-party module-object exception.** Tests/tools that need a module object
    for monkeypatching, reloading, or package-surface assertions may use
    `import myapp.main as main_module`. This is a module import, not a competing
    first-party symbol-import style.

### Enforcement (ruff)
Machine-enforced by `flake8-import-conventions` (`ICN`): `banned-from` forbids
`from <module> import ...` for the qualified set; `aliases` pins `numpy = "np"`
and `polars = "pl"`. Rationale: Google Python Style Guide §2.2 ("use `import`
for packages and modules only") for the qualified set; PEP 8 pragmatism for the
universal direct set (`typing`, `pathlib`, …).

## Package Exports (`__init__.py`)

Every package `__init__.py` has a single-line module docstring.

- **Namespace package** (no public surface): docstring only — no imports, no `__all__`.
- **Re-export hub**: docstring + explicit `from … import …` + `__all__`. `__all__`
    lists exactly the re-exported (and any locally-defined) public names — a bijection
    with the imports — and stays isort-sorted.
- Re-export via `from module import Name` + `__all__`, not redundant aliases.
- No parentheses around single-name imports.

Machine-enforced by ruff `RUF022` (sorted `__all__`) and `F401` (import hygiene).

## Type Annotations

### Required
- Full type annotations on **all** function signatures
- Include return types, even for `None`
- **Exception**: `__init__` methods must NEVER annotate a return type.
  The implicit `None` return is universally understood and adds noise.
  - Good: `def __init__(self, *, name: str):`
  - Bad: `def __init__(self, *, name: str) -> None:`
- When forward references are needed, use `from __future__ import annotations`
    and do not use string-literal forward references (for example `"AppConfig"`).

### Prohibited
- **No `Any` in production code** unless absolutely unavoidable
- **No `cast` in production code** — do not use `typing.cast`/`cast(...)`; refactor
    type boundaries instead
- Use `object` for truly unconstrained types
- Use proper unions (`str | int`) instead of `Any`

### Domain Scalar & Custom Types

Choose the lightest tier that fits. Define shared domain types in `core/types.py`
(or a layer-local `types.py` for presentation/scripts). Each tier has a fixed
trigger, so classification is never a judgment call:

| Tier | Use when | Example |
|------|----------|---------|
| **Validated value object** | The value carries an **enforceable invariant** that must hold at a trust boundary (config, request, persistence). Validate in `__new__` / `__post_init__`. | `MaxTokens(int)` > 0 ≤ 1_000_000, `Temperature` in [0, 2], `Confidence` in [0, 1], `CPR` |
| **Structural alias (`type`)** | Names a recurring **compound shape** (dict/tuple/callable) with no scalar invariant. | `type EmbeddingComponents = tuple[float, ...]`, `type JSONDict = dict[str, object]` |
| **Decoupling alias (`type`)** | A core stand-in for a value whose concrete type is an **enum owned by an outer layer** that core must not import. | `type ModelDeploymentName = str` (a `ChatModel` value), `type StrategyName = str` (a `RagStrategy` value) |
| **`NewType`** | An opaque scalar **identifier** kept distinct for the checker, no arithmetic, no runtime invariant. Requires explicit wrapping `X(value)`. | `UserId = NewType("UserId", int)` |
| **Bare primitive** | A local, measured, or computed value with no boundary invariant: counts in arithmetic, free text, one-off collections. | `int`, `str`, `tuple[float, float]` |

- A measured/computed **output** you receive (a provider token count, a `len()`
  chunk count) is a primitive; when it lives inside a value object, that object
  validates it (`RetrievalDiagnostics` rejects negative counts). A constrained
  **input** you set (a max-token limit) is a value object. This is why `MaxTokens`
  is a value object while token/chunk counts are primitives.
- Retrieval-specific application: `RetrievalQuery.max_context_tokens` is a
    constrained input budget and uses `MaxTokens`; `RetrievalDiagnostics`
    counters stay primitive `int` outputs.
- An internal knob sourced only from a validated module constant (for example
  `RAG_TOP_K: Final[int]`) does not cross a trust boundary and stays a bare
  primitive; `top_k`, `chunk_size`, and `chunk_overlap` are `int`, not value
  objects.
- Never create a scalar type alias purely for documentation (e.g.
  `PromptContent = str`): it adds neither safety nor distinctness. Use a
  primitive with a descriptive name, or promote to `NewType`/a value object.
- Add Pydantic schema hooks (`__get_pydantic_core_schema__`) to a value object
  **only** when it is used as a model field (as `Confidence` is);
  construction-only types (`MaxTokens`, `Temperature`) omit them.

### Annotated-first Metadata
- Prefer `typing.Annotated` for FastAPI request/dependency metadata:
    `Annotated[..., Query/Path/Body/Header/Cookie/Form/File/Depends(...)]`.
- Reuse a shared dependency as a plain module-level `Annotated` assignment
    (`MetricsDep = Annotated[MetricsPort, Depends(_get_metrics)]`), not a `type`
    alias — FastAPI introspects the assigned value at request time.
- Prefer `Annotated[..., Field(...)]` for Pydantic constraints/schema metadata
    when default/alias constructor synthesis is not required.
- Prefer assignment form (`field: Type = Field(...)`) for
    `default`, `default_factory`, and `alias` so static checkers synthesize accurate
    model constructors.
- Avoid legacy FastAPI default-style declarations in new code, e.g.
    `param: str = Query(...)`.

## Function Signatures

### Keyword-Only Arguments
Use `*` separator when function has **3 or more** parameters:

```python
# Good: 3+ parameters use keyword-only
def create_order(
    customer_id: str,
    *,
    product_id: str,
    quantity: int,
    amount: float
) -> Order:
    pass

# Good: 1-2 parameters can be positional
def get_order(order_id: str) -> Order:
    pass
```

## Dataclasses

### Immutability
- Use `kw_only=True` for **all** dataclasses
- Use `@dataclass(frozen=True, kw_only=True, slots=True)` for **all** domain entities and value objects
- Use `slots=True` for mutable dataclasses when compatible (no required dynamic attributes and no incompatible inheritance constraints)
- **Exception**: `Container` and mutable service classes may omit `frozen`
- Prefer `@property` for computed attributes. `@cached_property` requires a
  `__dict__` and is incompatible with `slots=True`; reserve it (on non-slotted
  classes) for expensive, stable computations or lazily-memoized singletons
  such as `Container`.

```python
from dataclasses import dataclass
from typing import final

# Good: Immutable domain entity
@final
@dataclass(frozen=True, kw_only=True, slots=True)
class Email:
    value: str

    def __post_init__(self):
        if "@" not in self.value:
            raise ValueError("Invalid email format")

# Good: Immutable DTO
@dataclass(frozen=True, kw_only=True, slots=True)
class OrderDTO:
    order_id: str
    customer_id: str
    status: str
```

## Final and Override

Make inheritance intent explicit with `typing.final` and `typing.override`.
Import both from `typing` (never `typing_extensions`; target is 3.13+).

### `@final`
Decorate every **public** concrete leaf that is logic- or invariant-bearing and
**not** designed for subclassing — domain scalars and value objects (`CPR`,
`MaxTokens`, `Temperature`, `Confidence`, `WorkerCount`), entities, services,
orchestrators, concrete handlers, clients, repositories, stores, managers, the
container, public middleware and logging filters/formatters, per-environment
configs. Never on an ABC, a `Protocol`, or an extension base (`CaseHandlerBase`,
`RepositoryBase`, `_ConfiguredDTOModel`, a subclassed base DTO). Also valid on a
**method** subclasses must not override (`CaseHandlerBase._query_ai_model`).

Skip `@final` on two orthogonal grounds: (1) internal (`_`-prefixed) classes — the
underscore already signals "implementation detail" (`_ExtraFormatter`); and (2)
pure data-shape types — DTOs, enums, ORM models, `NamedTuple`s (e.g. public
`Rectangle`) — which own no invariant to protect, **public or not**. The line is
*invariant/logic-bearing* vs *pure-shape*, not public vs internal: `MaxTokens`
(value object) earns `@final`; `Rectangle` (shape tuple) does not — both public.

### `@override`
Decorate a method that overrides one from a concrete or ABC base — abstract-method
implementations and framework overrides:

```python
from typing import final, override


@final
class ContextInjectingFilter(logging.Filter):
    @override
    def filter(self, record: logging.LogRecord) -> bool: ...
```

Do **not** use `@override` for `__init__`/`__new__`/`__post_init__`, a *new*
`@abstractmethod`, or a method that only satisfies a structural `Protocol` port
(implementing a port fulfils an interface — it does not override behavior — so
`ChatClient`, the repositories, and the stores stay undecorated). Internal
underscore classes follow the same rules. Order: `@final` above `class`;
`@override` directly above `def`.

## Naming and Module Layout

Names encode intent and layer — a reader predicts the class from the filename and
vice versa (PEP 8).

- **Internal vs public**: a single leading underscore marks a non-public module,
  class, function, or constant (`_base.py`, `_ErrorResponse`, `_mask_cpr`,
  `_MAX_TOKENS_LIMIT`). Public names carry no underscore and are listed in
  `__all__`. A `from_config` view Protocol is always private (`_ChatConfig`).
- **One public class per behavioral module**: handlers, clients, ports,
  repositories, stores, orchestrators, services, managers, configs, and the
  container define exactly one public class, and the filename is the `snake_case`
    of it — `diagnosis_date_handler.py` → `DiagnosisDateHandler`, `container.py` →
  `Container`. Private helpers (a `_XConfig` Protocol, a helper `NamedTuple`) sit
  in the same module with a `_` prefix.
- **Role suffix**: class names end in their layer role (`Port`, `Client`,
  `Repository`, `Store`, `Settings`, `Config`, `Handler`, `Orchestrator`,
  `Service`, `Manager`). The suffix is dropped from the filename when the folder
    names the role (`ports/clients/chat.py` → `ChatPort`, `repositories/case.py` →
  `CaseRepository`) and kept when it reads better (`*_handler.py`).
- **Data types group by theme**: DTOs, enums, ORM models, and value types share a
  themed module (`case.py`, `enums.py`, `models.py`), not one class per file.
- **Casing**: `PascalCase` classes with acronyms fully upper (`HTTPLogger`,
  `CPR`); `snake_case` modules/functions/variables; `SCREAMING_SNAKE_CASE`
  constants (internal untyped); exceptions end in `Error`.

## Enums

All enums must:
- Extend `StrEnum`
- Use `@unique` decorator
- Use `auto()` for value generation

```python
from enum import StrEnum, auto, unique

@unique
class StatusCode(StrEnum):
    NEW = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
```

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

## Constants

```python
from typing import Final

# Good: Typed constant
MAX_RETRY_ATTEMPTS: Final[int] = 3
DEFAULT_TIMEOUT: Final[float] = 30.0
API_VERSION: Final[str] = "v1"

# Good: Internal constant (no type annotation)
_RETRY_BACKOFF_SECONDS = 0.5

# Bad: Untyped
MAX_RETRY_ATTEMPTS = 3

# Bad: Using Final annotation (redundant)
MAX_RETRY_ATTEMPTS: Final = 3

# Bad: Typed internal constant
_RETRY_BACKOFF_SECONDS: float = 0.5
```

## Logging

### Use stdlib logging
```python
import logging

_logger = logging.getLogger(__name__)

# Good: %-style structured logging
_logger.info("order_processed order_id=%s duration_ms=%.2f", order_id, duration)

# Bad: print statements
print(f"Processing order {order_id}")

# Bad: f-strings in log calls
_logger.info(f"Processing order {order_id}")
```

### No Emojis
- **Never** use emojis in logs, code, or docstrings
- Keep output professional and parseable

## Docstrings

### Google-Style Format
```python
def process_order(order_id: str, *, amount: float, priority: int) -> OrderResult:
    """Process an order and return the result.

    Args:
        order_id (str): Unique identifier for the order.
        amount (float): Order amount in local currency.
        priority (int): Processing priority (1-5, higher is more urgent).

    Returns:
        OrderResult: Processed order with status and details.

    Raises:
        ValidationError: If order_id is invalid or amount is negative.
        DatabaseError: If database operation fails.
    """
    pass
```

### Docstring Rules
1. **All public functions/classes** must have docstrings
2. **`Args:`** section must include type hints in parentheses
3. **`Returns:`** section must include return type
4. **`Raises:`** section must only document exceptions **raised directly** in the function body
   - Do **not** document transitive exceptions from called functions
5. Use **single quotes** for identifiers: `'ClassName'`, not `` `ClassName` ``
6. **Never** start sentences with articles (a, an, the)
7. Use triple-quoted docstrings (`"""..."""`) for all docstrings, including
    single-line summaries.
    - Good: `"""Case identifier."""`
    - Bad: `"Case identifier."`
8. **Never** start docstring summary lines with any of these words:
   "Return", "Returns", "Response", "Request", "Payload"
   - Use a descriptive noun-phrase or imperative verb instead
    - Good: `"""Case identifier."""` or `"""Provide helper for inserting rows."""`
    - Good: `"""Successful case creation payload."""` or `"""New case creation data."""`
   - Bad: `"""Return case identifier."""` or `"""Returns the case ID."""`
   - Bad: `"""Response returned after case creation."""` or `"""Response for upload."""`
   - Bad: `"""Request payload for creating a customer."""` or `"""Payload for\u2026"""`
9. **Property docstrings** use simple noun-phrase one-liners describing what the
   property represents. Do not add `Returns:` sections to property docstrings.
    - Good: `"""Unique case identifier."""`
   - Bad: `"""Return case identifier.\n\n    Returns:\n        UUID: ...\n    """`
10. **Route handlers** use simple one-liner docstrings when the route decorator
   provides `description=`. Do not duplicate endpoint documentation in the docstring.
    - Good: `"""Create a case record."""`
   - Bad: Multi-line docstrings restating the decorator description

```python
# Bad: Missing types
def process(data):
    """Process the data.

    Args:
        data: The input data.

    Returns:
        The processed result.
    """
    pass

# Good: Complete types and no articles
def process(data: dict) -> ProcessResult:
    """Process input data and return structured result.

    Args:
        data (dict): Input data.

    Returns:
        ProcessResult: Structured result with status and details.
    """
    pass
```

## Error Handling

### Exception Chaining
```python
# Good: Preserve exception context
try:
    result = risky_operation()
except ValueError as e:
    raise ProcessingError("Failed to process data") from e

# Bad: Loses original exception
try:
    result = risky_operation()
except ValueError:
    raise ProcessingError("Failed to process data")
```

### Specific Exceptions
```python
# Good: Catch specific exceptions
try:
    data = json.loads(raw_data)
except json.JSONDecodeError as e:
    logger.error("invalid_json", error=str(e))
    raise

# Bad: Bare except
try:
    data = json.loads(raw_data)
except:
    logger.error("error")
```

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Functions, methods | `snake_case` | `process_case()` |
| Classes | `PascalCase` | `CaseRepository` |
| Constants | `SCREAMING_SNAKE_CASE` | `MAX_RETRIES` |
| Type aliases | `PascalCase` | `JSONDict` |
| Protocols | `PascalCase` with `Protocol` suffix | `CaseRepositoryProtocol` |
| Module files | `snake_case.py` | `case_service.py` |

### Terminology

Use the acronym `DTO`/`DTOs` in prose, docstrings, and docs. The expanded form
"data transfer objects" appears exactly once, in the `myapp.application.dtos`
package docstring. Do not describe DTO classes as "Pydantic models", "schemas",
or "payload models".

## Code Hygiene

### Remove Dead Code
- No commented-out code blocks
- No unused imports
- No dead/unreachable code
- Remove in the **same changeset** as the refactoring

### No TODOs Without Issues
```python
# Bad: Vague TODO
# TODO: Fix this later

# Good: Linked to issue
# TODO(#123): Implement retry logic for transient errors
```

## HTTP Status Codes

```python
from fastapi import status

# Good: Named constant
return JSONResponse(status_code=status.HTTP_200_OK, content=data)

# Bad: Magic number
return JSONResponse(status_code=200, content=data)
```

## Imports

### Organization
```python
# 1. Standard library
import sys
from datetime import datetime
from pathlib import Path

# 2. Third-party
from fastapi import FastAPI, Depends
from pydantic import BaseModel

# 3. Local application
from core.entities.order import Order
from application.services.order_service import OrderService
```

### No Wildcard Imports
```python
# Bad
from core.enums import *

# Good
from core.enums import StatusCode, OrderType
```
