---
name: python-conventions
description: Python standards for typing, logging, and maintainability.
paths:
  - "**/*.py"
---

# Skill: Python Conventions

## Technology Stack

| Aspect | Standard |
|--------|----------|
| Language | Python 3.12 |
| Package manager | `uv` |
| Type checker | `ty` (Astral) |
| Linter/formatter | Ruff |
| Logging | `structlog` |
| Settings | Pydantic `BaseSettings` |
| ORM | SQLAlchemy 2.0+ async |
| Enums | `ParseableEnum(StrEnum)` base class |
| Dataclasses | `@dataclass(frozen=True, slots=True)` |

## Non-Goals

- Do NOT use `Any` in production type annotations
- Do NOT use `print()` for logging or debugging
- Do NOT use bare `dict[str, ...]` — use `BaseDict` / `JSONDict` aliases
- Do NOT leave commented-out code blocks
- Do NOT add compatibility wrappers for retired patterns

---

## Type Hints

### Full Annotations

Every function, method, and variable with non-obvious type must have explicit
type annotations. No implicit `Any` from missing annotations.

```python
# Good
def process_audio(
    *,
    buffer: bytes,
    sample_rate: int,
    channels: int,
) -> TranscriptionResult:
    ...

# Bad — missing return type, implicit Any
def process_audio(buffer, sample_rate, channels):
    ...
```

### `Final` Constants

Module-level constants must use `Final[type]`:

```python
from typing import Final

MAX_RETRIES: Final[int] = 3
DEFAULT_MODEL: Final[str] = "gpt-4o"
SUPPORTED_FORMATS: Final[frozenset[str]] = frozenset({".wav", ".mp3", ".ogg"})
```

### `@final` Classes

Use `@final` to seal classes that must not be subclassed:

```python
from typing import final

@final
@dataclass(frozen=True, slots=True)
class AudioSegment:
    """Immutable audio segment. Not intended for subclassing."""
    data: bytes
    duration_ms: int
```

### No `Any`

Never use `Any` in production code. Alternatives:

| Instead of `Any` | Use |
|-------------------|-----|
| Unknown type | `object` |
| Generic container | `T = TypeVar("T")` with generics |
| Callback signature | `Protocol` with `__call__` |
| Mixed dict values | `JSONDict` alias |
| Plugin interface | `Protocol` class |

---

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Functions, methods | `snake_case` | `get_transcription()` |
| Variables | `snake_case` | `audio_buffer` |
| Classes | `PascalCase` | `TranscriptionService` |
| Constants | `SCREAMING_SNAKE_CASE` | `MAX_BUFFER_SIZE` |
| Type aliases | `PascalCase` | `Transcription = list[TranscriptionEntry]` |
| Protocols | `PascalCase` + `Protocol` suffix | `STTServiceProtocol` |
| Private | `_leading_underscore` | `_parse_header()` |
| Module files | `snake_case.py` | `audio_streamer.py` |

---

## Dataclasses

Always use `@dataclass(frozen=True, slots=True)` for immutability and memory
efficiency. The **only exception** is `Container`, which omits `slots=True`
because `cached_property` requires `__dict__`.

```python
from dataclasses import dataclass

# Standard — immutable value object
@dataclass(frozen=True, slots=True)
class TranscriptionEntry:
    """A single transcription segment with offset."""
    text: str
    offset: float

# Exception — Container needs __dict__ for cached_property
@dataclass
class Container:
    settings: BaseAppConfig
```

---

## Pydantic Models

Use `Annotated` + `Field` for validation metadata. Configure immutability via
`model_config`:

```python
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field

class AudioConfig(BaseModel):
    """Audio processing configuration."""

    model_config = ConfigDict(frozen=True)

    sample_rate: Annotated[int, Field(ge=8000, le=48000, description="Sample rate in Hz")]
    channels: Annotated[int, Field(ge=1, le=2, description="Mono or stereo")]
    format: Annotated[str, Field(pattern=r"^\.(wav|mp3|ogg)$")]
```

For settings, extend `BaseAppConfig` (which inherits from `BaseSettings`):

```python
from ekko.config.settings import BaseAppConfig

class LocalConfig(BaseAppConfig):
    """Local development settings."""
    debug: bool = True
```

---

## Logging

Use `structlog` exclusively. Never use `print()` or bare `logging`.

```python
import structlog

log: structlog.stdlib.BoundLogger = structlog.get_logger()

# Structured key-value context
log.info("transcription_complete", duration_ms=elapsed, word_count=len(words))
log.warning("retry_attempt", attempt=attempt, max_retries=MAX_RETRIES)
log.error("pipeline_failed", stage="pii_scrub", error=str(exc))
```

### Rules

- Bind loggers at module level: `log = structlog.get_logger()`
- Use snake_case keys in structured events
- Include relevant context as keyword arguments
- Use appropriate log levels: `debug`, `info`, `warning`, `error`, `critical`

---

## Keyword-Only Arguments

When a function has **3 or more parameters**, use the `*` separator to force
keyword-only usage. This prevents positional argument bugs.

```python
# Good — keyword-only after *
def create_transcription(
    *,
    audio_data: bytes,
    model: str,
    language: str,
) -> Transcription:
    ...

# Also good — 2 params, no separator needed
def add(a: int, b: int) -> int:
    return a + b

# Bad — 3+ params without * separator
def create_transcription(audio_data: bytes, model: str, language: str) -> Transcription:
    ...
```

---

## Exception Handling

### Always Chain Exceptions

Use `raise ... from original_error` to preserve the causal chain:

```python
try:
    result = await client.transcribe(audio)
except httpx.HTTPStatusError as exc:
    raise TranscriptionError(
        f"Transcription API returned {exc.response.status_code}"
    ) from exc
```

### Catch Specific Exceptions

Never use bare `except:` or `except Exception:` without good reason:

```python
# Good
try:
    config = load_config(path)
except FileNotFoundError as exc:
    raise ConfigurationError(f"Config not found: {path}") from exc
except json.JSONDecodeError as exc:
    raise ConfigurationError(f"Invalid JSON in {path}") from exc

# Bad
try:
    config = load_config(path)
except Exception:
    pass
```

---

## Docstrings

Google-style docstrings. The `Raises:` section must **only** list exceptions
raised directly in the function body (not exceptions from callees).

```python
def parse_audio_format(
    *,
    raw_format: str,
    strict: bool,
) -> AudioFormat:
    """Parse a raw format string into a validated AudioFormat.

    Args:
        raw_format: The file extension or MIME type to parse.
        strict: When True, reject unknown formats instead of
            falling back to defaults.

    Returns:
        The validated AudioFormat value object.

    Raises:
        ValueError: If strict is True and the format is unrecognized.
    """
    ...
```

---

## Dictionary Type Aliases

Use project type aliases instead of bare `dict[str, ...]`:

```python
from ekko.core.types import BaseDict, JSONDict

# BaseDict = dict[str, object]  — generic string-keyed dict
# JSONDict = dict[str, Any]     — JSON-compatible dict (only where serialization requires it)

def build_metadata(*, source: str, timestamp: float) -> BaseDict:
    return {"source": source, "timestamp": timestamp}
```

---

## String Constants

Extract repeated strings into `Final[str]` constants or use registry constants
from `core/registry_constants.py`:

```python
from typing import Final

# Module-level constants
DEFAULT_LANGUAGE: Final[str] = "en"
TRANSCRIPTION_ROUTE: Final[str] = "/api/v1/transcriptions"

# Or use generated registry constants
from ekko.core.registry_constants import AUDIO_FORMAT_WAV
```

Never scatter raw string literals across the codebase.

---

## Enums

All string enums extend `ParseableEnum(StrEnum)` from `core/enums/base.py`.
Use `@unique` and `auto()`:

```python
from enum import auto, unique

from ekko.core.enums.base import ParseableEnum

@unique
class AudioFormat(ParseableEnum):
    """Supported audio formats."""
    WAV = auto()
    MP3 = auto()
    OGG = auto()

# Case-insensitive parsing via inherited from_str()
fmt = AudioFormat.from_str("wav")  # AudioFormat.WAV
```

---

## HTTP Status Codes

Use `fastapi.status` constants, never raw integers:

```python
from fastapi import status

@router.post("/transcriptions", status_code=status.HTTP_201_CREATED)
async def create_transcription(...):
    ...

# Bad
@router.post("/transcriptions", status_code=201)
```

---

## Quick Checklist

- [ ] All functions have full type annotations (params + return)
- [ ] No `Any` in production code
- [ ] Constants use `Final[type]`
- [ ] Dataclasses use `frozen=True, slots=True`
- [ ] Functions with 3+ params use `*` separator
- [ ] Exceptions chained with `from original_error`
- [ ] Logging uses `structlog`, never `print()`
- [ ] Docstrings follow Google style
- [ ] String literals extracted to constants or registry
- [ ] Enums extend `ParseableEnum` with `@unique` + `auto()`
- [ ] Pydantic models use `Annotated + Field` and `ConfigDict(frozen=True)`
