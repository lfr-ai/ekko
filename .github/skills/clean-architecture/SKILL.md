---
name: clean-architecture
description: Enforce Clean Architecture boundaries and dependency direction.
paths:
  - "backend/src/ekko/**/*.py"
---

# Skill: Clean Architecture

## Dependency Direction

Dependencies always flow **inward**. Outer layers depend on inner layers,
never the reverse. The `core/` layer has zero framework imports.

```text
config -> core -> {ai | infrastructure} -> application -> presentation -> composition -> cli
```

`ai/` and `infrastructure/` are independent sibling adapter layers.

---

## Import Rules

| Layer | May Import From | NEVER Imports From |
|-------|----------------|--------------------|
| `config/` | external libs, stdlib | `core/`, `infrastructure/`, `ai/`, `application/`, `presentation/` |
| `core/` | `config/`, stdlib (+ Pydantic hooks) | `infrastructure/`, `ai/`, `application/`, `presentation/` |
| `infrastructure/` | `core/`, `config/`, external libs | `ai/`, `application/`, `presentation/` |
| `ai/` | `core/`, `config/` | `infrastructure/`, `application/`, `presentation/` |
| `application/` | `core/`, `infrastructure/`, `ai/`, `config/` | `presentation/` |
| `presentation/` | `application/`, `core/`, `config/` | `infrastructure/`, `ai/`, `composition/` |
| `composition/` | all layers (DI wiring) | — |
| `cli/` | `composition/`, `presentation/`, `config/` | entry point |

### Import Examples

```python
# GOOD — core imports from config (inner layer)
# core/entities/transcription.py
from ekko.config.settings import BaseAppConfig

# GOOD — application imports from core (inner layer)
# application/services/summarizer_service.py
from ekko.core.ports import ChatPort

# GOOD — presentation imports from application
# presentation/api/routes/transcription.py
from ekko.application.services.summarizer_service import SummarizerService

# BAD — core importing from application (outward dependency!)
# core/entities/transcription.py
from ekko.application.dtos import TranscriptionDTO  # VIOLATION

# BAD — infrastructure importing from presentation
# infrastructure/db/models.py
from ekko.presentation.api.dependencies import get_db  # VIOLATION

# BAD — ai importing from infrastructure
# ai/chains/summarize.py
from ekko.infrastructure.db.engine import get_session  # VIOLATION
```

---

## What Each Layer Contains

### `config/` -- Configuration

Pydantic `BaseSettings` classes, environment-based overrides, `.env` loading.

### `core/` -- Domain layer

The heart of the application. Pure business logic with no framework coupling.

| Directory | Purpose |
|-----------|---------|
| `entities/` | Domain entities (identity + behavior) |
| `value_objects/` | Immutable value objects (identity by value) |
| `ports/` | Port protocols (abstract boundaries) |
| `policies/` | Pure domain policy and rule evaluation |
| `exceptions/` | Domain exception hierarchy |
| `enums/` | Domain enumerations |
| `protocols.py` | Shared protocols |
| `registry_constants.py` | Generated naming constants |

### `infrastructure/` -- Adapters (outbound)

Concrete implementations of ports defined in `core/ports/`. Talks to
external systems: databases, APIs, file systems, audio hardware.

| Directory | Purpose |
|-----------|---------|
| `adapters/` | Audio, STT adapters |
| `concurrency/` | Queue and thread managers |
| `db/` | SQLAlchemy engine, ORM models, repositories |
| `llm/` | LLM chat adapters |
| `stt/` | Speech-to-text transcriber |

### `ai/` -- AI vertical

AI-specific implementations: conversational chains, PII scrubbing.
Depends on `core/` ports, not on `infrastructure/`.

| Directory | Purpose |
|-----------|--------|
| `chains/` | Conversational chains (LiteLLM-backed) |
| `pii/` | PII anonymization (regex-based) |
| `prompts/` | Prompt registry, templates, and versioning |

### `application/` -- Use cases & orchestration

Application services that coordinate domain objects and infrastructure.
Contains DTOs, handlers, mappers, and service classes.

| Directory | Purpose |
|-----------|---------|
| `dtos/` | Data transfer objects (API boundary) |
| `handlers/` | Application command/query handlers |
| `mappers/` | Entity <-> DTO mappers |
| `services/` | Orchestration services |

### `composition/` -- DI wiring

The `Container` dataclass and app factory. Wires concrete implementations
to abstract ports.

### `presentation/` -- Inbound adapters

FastAPI routes, GraphQL schema, middleware, dependency injection callables.
The outermost layer — nothing else imports from here.

---

## Port / Adapter Pattern

Ports (interfaces) are defined in `core/ports/` as Python `Protocol`
classes. Adapters (concrete implementations) live in `infrastructure/` or `ai/`.

```python
# PORT — core/ports/external/stt.py
from typing import Protocol

class STTService(Protocol):
    """Speech-to-text service port."""
    async def transcribe(self, audio: bytes) -> str: ...

# ADAPTER — infrastructure/adapters/stt_adapter.py
from ekko.core.ports import STTService

class AzureSpeechSTT:
    """Concrete STT adapter using Azure Speech."""
    async def transcribe(self, audio: bytes) -> str:
        # Implementation using the Azure Speech SDK
        ...
```

Application code depends on the protocol, never the concrete class:

```python
# application/services/transcription_service.py
from ekko.core.ports import STTService

class TranscriptionService:
    def __init__(self, *, stt: STTService) -> None:
        self._stt = stt  # Depends on protocol, not concrete adapter
```

---

## DI Container Pattern

The `Container` class in `composition/container.py` uses `@cached_property`
to lazily build and cache service instances:

```python
from dataclasses import dataclass
from functools import cached_property
from typing import final

@final
@dataclass
class Container:
    """Application-scoped DI container.

    Each service is built once on first access and reused for
    the lifetime of the container.

    Note: slots=True is omitted because cached_property requires __dict__.
    """

    settings: BaseAppConfig

    @classmethod
    def from_config(cls) -> Container:
        """Build a container from the current environment settings."""
        return cls(settings=get_settings())

    @cached_property
    def stt_service(self) -> STTService:
        """Lazily build the STT service."""
        from ekko.infrastructure.adapters.stt_adapter import create_faster_whisper_stt
        return create_faster_whisper_stt(settings=self.settings)

    @cached_property
    def summarizer_service(self) -> SummarizerService:
        """Lazily build the summarizer service."""
        from ekko.application.services.summarizer_service import SummarizerService
        from ekko.infrastructure.adapters.prompt_adapter import RegistryPromptProvider
        return SummarizerService(
            gateway=self.chat_adapter,
            prompt_provider=RegistryPromptProvider(settings=self.settings),
        )
```

Key rules for the Container:

- Uses `@cached_property` for lazy, singleton-scoped instantiation
- Uses deferred imports (inside property body) to avoid circular dependencies
- Marked `@final` — never subclassed
- No `slots=True` (incompatible with `cached_property`)
- Exposed to presentation layer via `presentation/api/dependencies.py` using
  FastAPI `Depends()` callables

---

## Common Violations to Watch For

| Violation | Example | Fix |
|-----------|---------|-----|
| Outward dependency | `core/` imports from `application/` | Move shared type to `core/` |
| Framework in core | `core/` imports `fastapi` or `sqlalchemy` | Use stdlib or `Protocol` |
| Concrete in application | Service depends on `AzureSpeechSTT` | Depend on `STTService` protocol |
| Business logic in routes | Validation/orchestration in route handler | Move to `application/services/` |
| DB models in core | `core/entities/` uses SQLAlchemy columns | Separate domain entity from ORM model |
| Cross-layer circular | `A -> B -> A` across layers | Extract shared interface to inner layer |
| DI bypass | Direct instantiation instead of Container | Wire through `Container` + `Depends()` |

---

## Verification

Run the architecture boundary check:

```bash
task lint        # Ruff import rules catch violations
task typecheck   # Type checker validates protocol conformance
task check       # Full gate: lint + test:unit + typecheck + xenon
```

Ruff is configured (in `ruff.toml`) with import ordering and
banned-import rules that enforce layer boundaries at lint time.

---

## Quick Checklist

- [ ] New files are placed in the correct layer
- [ ] Imports do not violate the dependency direction table
- [ ] No circular dependencies introduced
- [ ] `core/` has zero framework imports (no FastAPI, SQLAlchemy, etc.)
- [ ] Application services depend on protocols, not concrete adapters
- [ ] Business logic lives in `application/` or `core/`, not in routes
- [ ] New adapters implement a protocol from `core/ports/`
- [ ] New services are wired through `Container` with `@cached_property`
- [ ] No direct instantiation of infrastructure in application code
