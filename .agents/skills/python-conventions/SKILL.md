---
name: python-conventions
description: 'Enforces project Python coding standards including type hints, structured logging, keyword-only args, and forbidden patterns like Any or print(). Use when writing or reviewing Python code.'
---

# Python Conventions Skill

## Type Hints

### Do

```python
# Builtin generics
items: list[str]
mapping: dict[str, int]
pair: tuple[str, int]
nullable: str | None

# Final for constants
from typing import Final
MAX_RETRIES: Final[int] = 3

# @final for sealed classes/methods
from typing import final

@final
class ImmutableConfig: ...
```

### Do NOT

```python
# Never import generic aliases from typing
from typing import List, Dict, Tuple, Optional, Union

# Never use Any
from typing import Any
value: Any  # Use object instead

# Never use cast
from typing import cast
typed_value = cast(str, value)

# Never use string-literal forward references
field: "AppConfig"
```

When forward references are required, use `from __future__ import annotations`
instead of quoted annotations.

## Imports

Pick one style **per package** and use it **everywhere** — never mix. Applies to
classes *and* functions.

### Direct — `from x import Y`
`typing`, `collections.abc`, `typing_extensions`, `dataclasses`, `enum`,
`pathlib`, `datetime`, `uuid`, `contextlib`; distinctive framework symbols
(`pydantic.BaseModel`, `fastapi.FastAPI`); all first-party `myapp.*`.

### Qualified — `import x` then `x.Y`
Stdlib utility modules (`logging`, `os`, `sys`, `json`, `re`, `asyncio`,
`hashlib`, `html`, `shutil`, `inspect`, `argparse`) and namespace-heavy
third-party (`httpx`, `litellm`, `fitz`, `duckdb`; `numpy as np`, `polars as pl`).

```python
# Good: qualified — namespace kept, unambiguous at call site
import logging
import httpx

_logger = logging.getLogger(__name__)
handler: logging.Handler
response: httpx.Response

# Bad: direct import of utility-module symbols; keep logging qualified
from logging import Filter, Handler, LogRecord   # ICN003 banned-from
from logging.handlers import TimedRotatingFileHandler  # project policy ban
from httpx import Response                        # ICN003 banned-from

# Good: direct — distinctive symbols
from pathlib import Path
from pydantic import BaseModel
```

Tests/tools that require a first-party module object for monkeypatching,
reloading, or package-surface assertions may use
`import myapp.main as main_module`. This does not permit importing first-party
symbols in mixed styles.

Enforced by ruff `flake8-import-conventions` (`ICN`): `banned-from` +
`aliases`. Basis: Google Style Guide §2.2 (qualified set) + PEP 8 pragmatism
(direct set).

## Package Exports (`__init__.py`)

Every package `__init__.py` has a single-line module docstring.

- **Namespace package** (no public surface): docstring only — no imports, no `__all__`.
- **Re-export hub**: docstring + explicit `from … import …` + `__all__`. `__all__`
  lists exactly the re-exported (and any locally-defined) public names — a bijection
  with the imports — and stays isort-sorted.
- Re-export via `from module import Name` + `__all__`, not redundant aliases.
- No parentheses around single-name imports.

Enforced by ruff `RUF022` (sorted `__all__`) + `F401` (import hygiene).

## Domain Scalar Types

Pick the lightest tier that fits; shared types live in `core/types.py`. Each tier
has a fixed trigger:

```python
from typing import NewType, Self


# Tier 1 - validated value object: enforce a boundary invariant in __new__.
class MaxTokens(int):
    def __new__(cls, value: int) -> Self:
        if not 0 < value <= 1_000_000:
            raise ValueError("'max_tokens' must be in (0, 1_000_000]")
        return super().__new__(cls, value)


# Tier 2 - structural alias: a recurring compound shape, no scalar invariant.
type EmbeddingComponents = tuple[float, ...]
type JSONDict = dict[str, object]

# Tier 3 - decoupling alias: a core stand-in for an outer-layer enum value that
# core must not import (application/infrastructure use the concrete enum).
type ModelDeploymentName = str  # a ChatModel / EmbeddingModel value
type StrategyName = str  # a RagStrategy value

# Tier 4 - NewType: an opaque scalar id kept distinct for the checker, no invariant.
UserId = NewType("UserId", int)

# Tier 5 - bare primitive: local/measured/computed value, counts in arithmetic,
# free text; a containing value object validates it.
prompt_tokens: int
system_prompt: str
```

- A constrained **input** you set (a limit) is a value object (`MaxTokens`); a
  measured **output** you receive (a count) is a primitive validated by its
  container. That is why `MaxTokens` is a value object while token counts are not.
- Retrieval-specific application: `RetrievalQuery.max_context_tokens` is a
    constrained input budget and should use `MaxTokens`; diagnostics counters
    (`prompt_tokens`, `retrieved_chunks`) remain primitive `int` outputs.
- An internal knob sourced only from a validated module constant (e.g.
    `RAG_TOP_K: Final[int]`) does not cross a trust boundary and stays a bare
    primitive; `top_k`, `chunk_size`, `chunk_overlap` are `int`, not value objects.
- Never create a scalar type alias just for documentation (e.g.
  `PromptContent = str`) — use a primitive or promote to `NewType`/a value object.
- Add Pydantic hooks to a value object only when it is a model field (`Confidence`).

## Dataclasses

Use `frozen=True, kw_only=True, slots=True` for immutable classes; mutable
classes may omit `frozen` but remain keyword-only:

```python
from dataclasses import dataclass

@dataclass(frozen=True, kw_only=True, slots=True)
class Config:
    host: str
    port: int
    timeout: float = 30.0
```

## Enums

Always `@unique` and use `StrEnum`:

```python
from enum import StrEnum, unique

@unique
class Status(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
```

## Logging

Use Python stdlib `logging` with a module-scoped logger:

```python
import logging

_logger = logging.getLogger(__name__)

_logger.info("processing_request request_id=%s", request_id)
_logger.error("validation_failed reason=%s", reason)
_logger.exception("unexpected_error resource_id=%s", resource_id)
```

## Async SQLAlchemy

Use async session and query patterns:

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import select

async def get_entity(session: AsyncSession, entity_id: int) -> Entity | None:
    """Retrieve entity by ID."""
    stmt = select(Entity).where(Entity.id == entity_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def create_entity(session: AsyncSession, data: dict) -> Entity:
    """Create new entity."""
    entity = Entity(**data)
    session.add(entity)
    await session.commit()
    await session.refresh(entity)
    return entity
```

## Exception Handling

Specific catches with chaining:

```python
try:
    result = process(data)
except ValidationError as e:
    logger.error("Validation failed for %s", data_id, exc_info=True)
    raise ProcessingError("Invalid data") from e
except DatabaseError as e:
    raise StorageError("Database operation failed") from e
```

## Function Signatures

Keyword-only args with `*` for 3+ params:

```python
def process_request(
    request_id: int,
    *,
    validate: bool = True,
    strict_mode: bool = False,
    timeout: float = 30.0,
) -> ProcessResult:
    """Process request with configurable validation."""
```

## Docstrings (Google Convention)

```python
def validate_identifier(identifier: str) -> bool:
    """Validate identifier format and checksum.

    Args:
        identifier: Identifier string to validate.

    Returns:
        True if identifier is valid.

    Raises:
        ValueError: If identifier format is invalid.
    """
```

Rules:
- NEVER start sentences with articles ("a", "an", "the")
- NEVER start docstring summary with "Return", "Returns", "Response", "Request", or "Payload"
- Use triple-quoted `"""..."""` for all docstrings, including single-line
  summaries (enforced by ruff `D300` + the formatter)
- Complete sentences with periods
- Short, concise — avoid redundancy
- Property docstrings use noun-phrase one-liners (no `Returns:` section)
- Route handlers use one-liner docstrings when `description=` is present

## `__init__` Methods

`__init__` methods must NEVER annotate a return type:

```python
# Good
def __init__(self, *, name: str):
    self._name = name

# Bad
def __init__(self, *, name: str) -> None:
    self._name = name
```

## Pydantic Models

```python
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field

class ItemModel(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    description: Annotated[
        str | None,
        Field(
            default=None,
            min_length=1,
            max_length=500,
            description="Item description",
            examples=["Sample item"],
        ),
    ]
```

## Configuration & `from_config`

`*Settings` = an environment-sourced facet that *owns* a cohesive group of
prefixed env fields (e.g. `MYAPP_*`) — a `BaseSettings` subclass composed into
the app config. `*Config` = a complete, assembled configuration (`AppConfig`, the
environment classes) **or a consumer's structural view of it**.

A component built from configuration exposes `from_config(cls, config: _XConfig)`
where `_XConfig` is a private structural `Protocol` (same module) of only the
fields it reads. It never imports the app config — the config satisfies `_XConfig`
structurally (PEP 544).

```python
# Good: consumer owns a compact structural view named _<Component>Config
from typing import Protocol, Self

class _EmailClientConfig(Protocol):
    smtp_host: str
    smtp_password: SecretStr

class EmailClient:
    @classmethod
    def from_config(cls, config: _EmailClientConfig) -> Self:
        return cls(host=config.smtp_host, password=config.smtp_password)

# Bad: importing the concrete app config couples infrastructure to the config layer
from myapp.config import AppConfig
def from_config(cls, config: AppConfig) -> Self: ...

# Bad: naming the consumer view *Settings (reserved for field-owning facets)
class _EmailClientSettings(Protocol): ...
```

## Naming Conventions

| Entity | Convention | Example |
|--------|-----------|---------|
| Files | snake_case | `my_module.py` |
| Classes | PascalCase | `OrderProcessor` |
| Functions | snake_case | `process_order` |
| Variables | snake_case | `order_count` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRIES` |
| Private | `_` prefix | `_internal_state` |

## Caching

Prefer `@property` for computed attributes. Use `@cached_property` only when the
class has a `__dict__` (never with `slots=True`) and the value is an expensive,
effectively-immutable computation or a lazily-memoized singleton that must return
the same instance on each access. To use `@cached_property` on a dataclass, omit
`slots=True`.

```python
from functools import lru_cache, cached_property

@lru_cache(maxsize=128)
def expensive_computation(key: int) -> str: ...

@dataclass(frozen=True, kw_only=True)  # no slots -> enables cached_property
class Container:
    @cached_property
    def db_client(self) -> DbClient: ...  # expensive singleton, memoized once
```

## Retry Policies

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1.5, min=2, max=15),
    reraise=True,
)
def call_api() -> dict[str, object]: ...
```

## Package Management

Use the repository's `uv` environment for dependency management and commands:

```bash
uv add httpx
uv add --dev pytest
uv sync
uv run pytest
```
