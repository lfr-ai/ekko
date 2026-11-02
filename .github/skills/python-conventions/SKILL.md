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
`pathlib`, `datetime`, `uuid`, `contextlib`, `functools` (`cached_property`,
`lru_cache`, `singledispatch`, `wraps`); distinctive framework symbols
(`pydantic.BaseModel`, `fastapi.FastAPI`); all first-party `myapp.*`.

### Qualified — `import x` then `x.Y`
Stdlib utility modules (`logging`, `os`, `sys`, `json`, `re`, `asyncio`,
`hashlib`, `html`, `shutil`, `inspect`, `argparse`) and namespace-heavy
third-party (`httpx`, `litellm`, `duckdb`; `numpy as np`, `polars as pl`).

```python
# Good: qualified — namespace kept, unambiguous at call site
import logging
import httpx

_logger = logging.getLogger(__name__)
handler: logging.Handler
response: httpx.Response

# Bad: direct import of utility-module symbols; keep logging qualified
from logging import Filter, Handler, LogRecord  # ICN003 banned-from
from logging.handlers import TimedRotatingFileHandler  # project policy ban
from httpx import Response  # ICN003 banned-from

# Good: direct — distinctive symbols
from pathlib import Path
from pydantic import BaseModel
```

Tests/tools that require a first-party module object for monkeypatching,
reloading, or package-surface assertions may use
`import myapp.main as main_module`. This does not permit importing first-party
symbols in mixed styles.

Enforced by ruff `flake8-import-conventions` (`ICN`) `banned-from`/`aliases`
for a Qualified-bucket module imported directly; the reverse (a Direct-bucket
module imported qualified, e.g. `import functools`) has no ruff rule and is
caught by `check_conventions.py`'s `qualified-direct-import-module` check.
Basis: Google Style Guide §2.2 (qualified set) + PEP 8 pragmatism (direct set).

## Package Exports (`__init__.py`)

Every package `__init__.py` has a single-line module docstring.

- **Namespace package** (no public surface): docstring only — no imports, no `__all__`.
- **Re-export hub**: docstring + explicit `from … import …` + `__all__`. `__all__`
  lists exactly the re-exported (and any locally-defined) public names — a bijection
  with the imports — and stays isort-sorted.
- Re-export via `from module import Name` + `__all__`, not redundant aliases.
- No parentheses around single-name imports.

Enforced by ruff `RUF022` (sorted `__all__`) + `F401` (import hygiene).

Dunder files and methods (`__new__`, `__eq__`/`__hash__`, `__slots__`, context
managers, Pydantic schema hooks): [references/dunder-patterns.md](references/dunder-patterns.md).

## Domain Scalar Types

Pick the lightest tier that fits; shared types live in `core/types.py`. See
[references/framework-patterns.md](references/framework-patterns.md) for the full
5-tier catalog with the retrieval-budget worked example.

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

Copy-and-rename starting point: [`assets/dataclass.py.template`](assets/dataclass.py.template)
(a plain, non-domain data holder — a domain entity/value object/event instead
uses the `ddd` skill's templates).

### Dataclass vs. plain class

Pick by role, not by how little code a plain `__init__` would take:

- **`@dataclass`** — the type's job is to **hold data**: field-wise equality,
  no behavior beyond validating itself in `__post_init__`, safe to copy/compare
  by value. Value objects, domain events, DTOs, configuration facets
  (`*Settings`/`*Config`), ORM-adjacent read snapshots/records, and structured
  Protocol return payloads all belong here.
- **Plain class (explicit `__init__`)** — the type's job is to **do** something:
  it holds injected collaborators/resources, has identity that matters more
  than field equality, or implements a `Protocol` port via inheritance +
  `@override`. Adapters/clients, repositories, orchestrators, services,
  handlers, the DI container, and anything with a `from_config` classmethod
  stay plain classes even when `__init__` is just a few attribute assignments —
  field-wise `__eq__` would be meaningless (or actively wrong) for a component
  identified by its injected dependencies, not their values.

One-line test: if two instances built from equal arguments should compare
equal and be interchangeable, it is a dataclass; if it wraps behavior/side
effects (I/O, a session, a client), it stays a plain class regardless of how
short its `__init__` is.

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

Copy-and-rename starting point: [`assets/enum.py.template`](assets/enum.py.template).

## Logging

Use Python stdlib `logging` with a module-scoped logger:

```python
import logging

_logger = logging.getLogger(__name__)

_logger.info("processing_request request_id=%s", request_id)
_logger.error("validation_failed reason=%s", reason)
_logger.exception("unexpected_error resource_id=%s", resource_id)
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

Pass the message straight to the constructor — never bind it to a `message`/
`msg` variable first, even for a long, line-wrapped string:

```python
# Bad
message = "No content returned."
raise EmptyChatCompletionError(message)

# Good
raise EmptyChatCompletionError("No content returned.")
```

`EM` (flake8-errmsg) is deliberately not enabled in `ruff.toml` — it would
force the Bad form above on every raise. Same rationale as the `TRY003` ignore.

A port earns its own exception (`core/ports/<category>/exceptions.py`) when an
adapter can fail in a way `ValueError`/`RuntimeError` doesn't capture precisely
(e.g. `EmptyChatCompletionError`, parallel to `PersistenceUnavailableError`) —
this keeps callers/tests decoupled from an overly generic stdlib exception.
One named type per distinct failure mode, never a shared generic type reused
across ports (`ChatClientPort` empty-completion vs. `OCRScannerClientPort`
no-extractable-text are different types despite both being "unusable result").

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

Drop the trailing comma so the formatter collapses a short signature onto one
line instead of forcing it multi-line — well-considered signatures often fit:

```python
# Good: fits in 88 chars -> one line, no trailing comma
def _record_http_request(*, status_code: int) -> None: ...


# Bad: forces multi-line for a signature that fits on one line
def _record_http_request(
    *,
    status_code: int,
) -> None: ...
```

Add `/` positional-only (PEP 570) for a parameter whose name is not part of
its meaning, and never write a Java-style `get_x()`/`set_x()` pair for plain
attribute access — use `@property` instead. Pick function/method verbs
(`get`/`load`/`fetch`/`pop`/`parse`/`coerce`/`extract`/`resolve`/`build`/
`process`/…) from the shared vocabulary, never a synonym. Details:
[references/signature-patterns.md](references/signature-patterns.md).

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
- NEVER start docstring summary with "Return", "Returns", "Response", "Request",
  "Payload", or "Raised" (exception docstrings state the error condition, not
  "Raised when...")
- Use triple-double-quoted `"""..."""` for all docstrings, including single-line summaries (Ruff formatter)
- Complete sentences with periods
- Short, concise — avoid redundancy
- Property docstrings use noun-phrase one-liners (no `Returns:` section)
- Route handlers use one-liner docstrings when `description=` is present

### Docstring depth

Docstrings default to brevity: a section (`Args`/`Returns`/`Raises`) earns
its place only when it carries meaning the signature/type can't already
show, and once any structured section is used, every warranted section must
be present — never a subset. The same brevity test governs whether a
module/class docstring stays one line or expands for real, STABLE
information (never a literal number mirroring a constant that goes stale).
Full rule and worked examples for both function/method and module/class
docstrings: [references/docstring-patterns.md](references/docstring-patterns.md).

## Polymorphism

Default to a `Protocol` port + `@override`-decorated adapters; reach for `ABC`
only when adapters share real executable code, not just a signature. A
growing `isinstance`/type-tag `if`/`elif` or `match` chain on an object's
*type* (not a closed, self-owned `StrEnum`) is an Open/Closed smell — replace
it with a Strategy, not more branches. Never introduce an abstraction for a
single existing implementation (speculative generality). `Protocol` is this
codebase's typed duck typing (PEP 544) — reach for untyped `hasattr` duck
typing only at a single dynamic call site; twice means use a `Protocol`. Full
decision table: [references/polymorphism-patterns.md](references/polymorphism-patterns.md);
member order: [references/method-ordering.md](references/method-ordering.md).

## `__init__` / `__post_init__` Methods

`__init__` and a dataclass's `__post_init__` must NEVER annotate a return type:

```python
# Good
def __init__(self, *, name: str):
    self._name = name


def __post_init__(self):  # noqa: ANN204
    if not self.name:
        raise ValueError("name must not be empty")


# Bad
def __init__(self, *, name: str) -> None:
    self._name = name


def __post_init__(self) -> None:
    if not self.name:
        raise ValueError("name must not be empty")
```

Ruff's `mypy-init-return` (`ruff.toml`) only suppresses ANN204 for `__init__`
when a non-`self` parameter is annotated — never for `__post_init__` or a
zero-parameter `__init__`, both of which need `# noqa: ANN204` instead of `-> None`.

`__init__` never gets a bare one-line docstring — the same all-or-nothing
rule from the brevity test applies, and "Initialize X with Y" restating the
parameter list adds nothing a reader can't already see. Exactly two shapes
(mechanically enforced by `scripts/check_conventions.py`'s
`init-docstring-shape` rule):

- **Zero parameters** (or `self` only) — omit the docstring; the convention
    guard enforces this shape because Ruff `D107` cannot distinguish it from a
    defect.
- **One or more parameters** — full `Args:` section documenting every
  parameter, same as any other method:

```python
# Good: no annotated param -> noqa instead of -> None
class SessionStore:
    def __init__(self):  # noqa: ANN204
        self._value_by_session_id: dict[UUID, str] = {}


# Good: annotated params -> mypy-init-return covers it, no noqa needed
class ChatClient:
    def __init__(self, *, model_provider: str, api_key: SecretStr):
        """Initialize client with chat provider connection parameters.

        Args:
            model_provider (str): LiteLLM provider prefix for deployments.
            api_key (SecretStr): Provider API key for authentication.
        """
        self._model_provider = model_provider
        self._api_key = api_key
```

## Framework Patterns

See [references/framework-patterns.md](references/framework-patterns.md) for
async SQLAlchemy sessions, concurrent-task lifecycle, shared async client
state (token-cache locking), Pydantic model conventions, and the
`*Settings`/`*Config`/`from_config` naming/Protocol pattern.

## Naming Conventions

| Entity | Convention | Example |
|--------|-----------|---------|
| Files | snake_case | `my_module.py` |
| Classes | PascalCase | `OrderProcessor` |
| Functions | snake_case | `process_order` |
| Variables | snake_case | `order_count` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRIES` |
| Private | `_` prefix | `_internal_state` |

### Module layout and layer-role suffixes

- One public class per behavioral module; the filename is that class in
  `snake_case` (`container.py` → `Container`). DTOs, enums, ORM models, and
  value types may instead share a themed module.
- Class names carry the layer role as a suffix — `Port`, `Client`,
  `Repository`, `Store`, `Settings`, `Config`, `Handler`, `Orchestrator`,
  `Service`, `Manager`. Drop the suffix from the *filename* only when the
  folder already names the role (`ports/clients/chat.py` → `ChatPort`).
- Acronyms are fully upper in `PascalCase` (`HTTPLogger`); exceptions end in
  `Error`. A `from_config` view `Protocol` is always private (`_ChatConfig`).
- Write `DTO`/`DTOs`, never "Pydantic models"/"schemas" — the expanded form
  appears once, in the `application.dtos` package docstring.

### No magic values

Extract a repeated or non-obvious literal (a threshold, a slice boundary, a
status code) to a named constant next to its first use. Enforced by ruff
`PLR2004`, relaxed in `tests/**` and internal `scripts/**` tooling (see
`ruff.toml` `per-file-ignores`).

## Caching

Prefer `@property` for computed attributes. Use `@cached_property` only when
the class has a `__dict__` (never with `slots=True`) and the value is an
expensive, effectively-immutable, or lazily-memoized singleton that must
return the same instance on each access — omit `slots=True` to enable it.

```python
from functools import cached_property


@dataclass(frozen=True, kw_only=True)  # no slots -> enables cached_property
class Container:
    @cached_property
    def db_client(self) -> DbClient: ...  # expensive singleton, memoized once
```

## Templates

[`assets/enum.py.template`](assets/enum.py.template) (`StrEnum` + `@unique` +
`Members:` section) and [`assets/dataclass.py.template`](assets/dataclass.py.template)
(plain, non-domain record dataclass, frozen and mutable variants).

## Verification

`uv run ruff check .` already enforces most of this skill (no `Any` via ANN401,
no `cast` via banned-api TID251, docstring presence/format via `D`, import style
via `ICN`). `scripts/check_conventions.py` covers the remaining ruff-blind spots
— quoted forward-reference annotations, `@dataclass` missing `kw_only=True`,
redundant `-> None` on `__init__`/`__post_init__`, banned docstring openers, an `__init__`
docstring breaking the two-shape rule (`init-docstring-shape`), and a type
annotation on an internal (underscore-prefixed) constant:

```shell
uv run python .agents/skills/python-conventions/scripts/check_conventions.py [path ...]
```

Defaults to scanning `src` and `tests` when no path is given. Exit code `0` = no
violations; non-zero prints each `file:line:rule` finding. This supplemental
audit is currently a standalone check: it is not wired into the Taskfile,
pre-commit, or CI. Ruff and the configured checks remain the enforced gates;
run this script manually when auditing the additional conventions.
