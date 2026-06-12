---
name: ddd
description: >
  Apply Domain-Driven Design patterns to Ekko's bounded contexts. Covers aggregates,
  value objects, domain events, repository protocols, domain services, and
  anti-corruption layers.
paths:
  - "backend/src/ekko/core/**/*.py"
  - "backend/src/ekko/application/**/*.py"
---

# Skill: Domain-Driven Design (DDD)

## Ekko Bounded Contexts

Ekko is divided into four bounded contexts. Each context has its own ubiquitous language.

| Context | Root Aggregate | Domain Language |
|---------|---------------|----------------|
| **Audio Processing** | `AudioSession` | session, chunk, recording, sample |
| **Transcription** | `Transcription` | entry, language, offset, duration |
| **Conversation** | `Conversation` | message, thread, role, turn |
| **AI Pipeline** | `SummaryJob` | summary, PII, embedding, prompt |

Bounded contexts communicate via application services, never via direct domain imports.

---

## Ubiquitous Language

Use these terms consistently in code, comments, and conversations.
Never substitute framework terms ("model", "row", "record") inside the domain layer.

| Term | Meaning |
|------|---------|
| `AudioSession` | A single continuous recording session |
| `AudioChunk` | A segment of raw audio bytes with timestamp |
| `Transcription` | Complete text output of a session |
| `TranscriptionEntry` | Single utterance: text, offset, duration |
| `Conversation` | A multi-turn AI dialogue |
| `Message` | A single turn in a conversation (user or assistant) |
| `SummaryJob` | Async task to summarize a transcription |
| `Language` | ISO 639-1 code with detection confidence |
| `PIISafeText` | Text guaranteed free of personal information |

---

## Aggregate Design

An **aggregate** is a cluster of domain objects treated as a single consistency unit.
The **aggregate root** is the only entry point for mutations.

### Rules

- Aggregates are `@dataclass(frozen=True, slots=True)` — immutable.
- All mutations return **new instances** (functional update style).
- Invariants are enforced in `__post_init__`.
- Keep aggregates small — only include what must be strongly consistent.
- One repository per aggregate root.

### Example: Transcription Aggregate

```python
# core/entities/transcription.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Final
from ekko.core.value_objects.language import Language
from ekko.core.value_objects.transcription_entry import TranscriptionEntry
from ekko.core.exceptions import TranscriptionError

_MAX_ENTRIES: Final[int] = 10_000


@dataclass(frozen=True, slots=True)
class Transcription:
    """Aggregate root for a complete transcription session.

    Invariants:
        - entries are ordered by offset ascending
        - total entries do not exceed _MAX_ENTRIES
    """

    id: int
    language: Language
    entries: tuple[TranscriptionEntry, ...]

    def __post_init__(self) -> None:
        if len(self.entries) > _MAX_ENTRIES:
            raise TranscriptionError(
                f"Transcription exceeds {_MAX_ENTRIES} entries",
            )
        offsets = [e.offset for e in self.entries]
        if offsets != sorted(offsets):
            raise TranscriptionError("Entries must be ordered by offset")

    @property
    def full_text(self) -> str:
        """Concatenated transcript as a single string."""
        return " ".join(e.text for e in self.entries)

    @property
    def duration_ms(self) -> float:
        """Total duration in milliseconds."""
        if not self.entries:
            return 0.0
        last = self.entries[-1]
        return last.offset + last.duration_ms

    def with_entry(self, entry: TranscriptionEntry) -> Transcription:
        """Return a new Transcription with the entry appended."""
        return Transcription(
            id=self.id,
            language=self.language,
            entries=(*self.entries, entry),
        )
```

---

## Value Objects

Value objects have **no identity** — equality is structural (all fields equal).
Use them for any domain concept defined by its attributes rather than an ID.

### Rules

- Always `@dataclass(frozen=True, slots=True)`.
- Validate all invariants in `__post_init__`.
- Place in `core/value_objects/`.
- No `id` field — identity comes from values.

### Example: Language Value Object

```python
# core/value_objects/language.py
from dataclasses import dataclass
from typing import Final
from ekko.core.exceptions import DomainValidationError

_SUPPORTED: Final[frozenset[str]] = frozenset({"en", "da", "de", "fr", "es", "nl"})


@dataclass(frozen=True, slots=True)
class Language:
    """ISO 639-1 language code with transcription confidence.

    Raises:
        DomainValidationError: If code is not supported or confidence is out of range.
    """

    code: str
    confidence: float = 1.0

    def __post_init__(self) -> None:
        if self.code not in _SUPPORTED:
            raise DomainValidationError(
                f"Unsupported language: {self.code!r}. Supported: {_SUPPORTED}",
            )
        if not 0.0 <= self.confidence <= 1.0:
            raise DomainValidationError(
                f"Confidence must be in [0, 1], got {self.confidence}",
            )
```

### Example: PIISafeText Value Object

```python
# core/value_objects/pii_safe_text.py
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PIISafeText:
    """Text guaranteed to be free of personally identifiable information.

    The original_hash allows audit trail without storing the raw PII.
    """

    value: str
    original_hash: str  # SHA-256 of pre-scrubbed text for audit
```

---

## Domain Events

Domain events capture **facts** — something significant that happened in the domain.
They are how bounded contexts communicate state changes without tight coupling.

### Rules

- Named in **past tense**: `TranscriptionCompleted`, not `CompleteTranscription`.
- Immutable `@dataclass(frozen=True, slots=True)`.
- Carry only **serializable primitives** — no domain objects as fields.
- Raised by aggregate methods, published via application services.
- Place in `core/events/`.

### Example Events

```python
# core/events/transcription_events.py
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class TranscriptionCompleted:
    """Raised when a full transcription is ready for downstream processing."""

    transcription_id: int
    language_code: str
    duration_ms: float
    entry_count: int
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class PIIDetected:
    """Raised when PII is found and scrubbed during anonymization."""

    transcription_id: int
    pii_type: str  # e.g. "EMAIL", "PHONE", "NAME"
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class RecordingStarted:
    """Raised when a new audio recording session begins."""

    session_id: int
    occurred_at: datetime
```

---

## Repository Protocol

Repositories abstract persistence behind a **domain-facing protocol**.
The protocol lives in `core/interfaces/`; the implementation in `infrastructure/db/repositories/`.

### Protocol (Port)

```python
# core/interfaces/transcription_repository.py
from typing import Protocol
from ekko.core.entities.transcription import Transcription


class TranscriptionRepository(Protocol):
    """Port for persisting and retrieving Transcription aggregates."""

    async def save(self, *, transcription: Transcription) -> None: ...
    async def get_by_id(self, *, transcription_id: int) -> Transcription | None: ...
    async def list_recent(self, *, limit: int) -> list[Transcription]: ...
    async def delete(self, *, transcription_id: int) -> None: ...
```

### Implementation (Adapter)

```python
# infrastructure/db/repositories/transcription_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from ekko.core.entities.transcription import Transcription


class SQLAlchemyTranscriptionRepository:
    """SQLAlchemy async implementation of TranscriptionRepository."""

    def __init__(self, *, session: AsyncSession) -> None:
        self._session = session

    async def save(self, *, transcription: Transcription) -> None:
        model = _to_orm_model(transcription)
        self._session.add(model)
        await self._session.flush()

    async def get_by_id(self, *, transcription_id: int) -> Transcription | None:
        model = await self._session.get(TranscriptionModel, transcription_id)
        return _to_domain(model) if model else None
```

### Repository Rules

- Protocols return **domain objects**, never ORM models.
- One repository per aggregate root.
- Implementations use keyword-only arguments (`*`) for all parameters.
- Mappers (`_to_orm_model`, `_to_domain`) are private module functions.

---

## Domain Services

Use a domain service when an operation spans multiple aggregates or has no
natural home in any single aggregate root.

```python
# core/services/pii_domain_service.py
from ekko.core.entities.transcription import Transcription
from ekko.core.interfaces.pii import PIIDetector


class PIIDomainService:
    """Coordinates PII detection across all entries of a Transcription aggregate."""

    def __init__(self, *, detector: PIIDetector) -> None:
        self._detector = detector

    async def anonymize(self, *, transcription: Transcription) -> Transcription:
        """Return a new Transcription with all PII replaced in every entry."""
        safe_entries = tuple(
            entry.with_safe_text(await self._detector.scrub(entry.text))
            for entry in transcription.entries
        )
        return Transcription(
            id=transcription.id,
            language=transcription.language,
            entries=safe_entries,
        )
```

---

## Anti-Corruption Layer

Translate **external system concepts** into domain terms at the infrastructure boundary.
This protects the domain from leaking foreign abstractions.

```python
# infrastructure/adapters/openai_acl.py
from ekko.core.interfaces.llm import LLMGateway
from ekko.core.value_objects.pii_safe_text import PIISafeText


class OpenAIAdapter:
    """Translates OpenAI API responses into Ekko domain types.

    This is the anti-corruption layer between the OpenAI SDK and domain code.
    """

    async def complete(self, *, prompt: PIISafeText) -> str:
        """Call OpenAI and return the assistant's reply as a plain string."""
        response = await self._client.chat.completions.create(
            model=self._model_id,
            messages=[{"role": "user", "content": prompt.value}],
        )
        return response.choices[0].message.content or ""
```

---

## Bounded Context Communication

Contexts **never import each other's domain objects**. They communicate via:

1. **Application services** — the primary integration point.
2. **Domain events** — published by one context, consumed by another.

```text
Audio Processing ──► Transcription   (TranscriptionService.create_from_session())
Transcription    ──► AI Pipeline     (SummaryService.summarize(transcription_id))
AI Pipeline      ──► Conversation    (ConversationService.append_summary(summary))
```

---

## Quick Checklist

- [ ] Aggregate roots are frozen dataclasses with invariant checks in `__post_init__`
- [ ] Value objects are `frozen=True, slots=True` with validated fields
- [ ] Domain events are past-tense frozen dataclasses with primitive fields only
- [ ] Repository protocols in `core/interfaces/` return domain objects (not ORM models)
- [ ] Implementations in `infrastructure/db/repositories/` use keyword-only args
- [ ] Domain services handle cross-aggregate operations
- [ ] Ubiquitous language used consistently — no "model", "row", "record" in domain
- [ ] Anti-corruption layers translate external concepts at the infrastructure boundary
- [ ] Bounded contexts communicate via application services, not direct domain imports
- [ ] No framework imports in `core/` (no FastAPI, SQLAlchemy, httpx)
