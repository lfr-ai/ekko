---
description: Domain-Driven Design patterns for the Ekko domain layer
applyTo: "backend/src/ekko/core/**/*.py"
---

# DDD Instructions

Apply these patterns to all code in `backend/src/ekko/core/`.

## Aggregates

- `@dataclass(frozen=True, slots=True)` on all aggregate roots.
- All invariants enforced in `__post_init__` — the aggregate is always valid after construction.
- Mutations return **new instances** — never modify state in-place.
- One repository per aggregate root (protocol in `core/interfaces/`).

## Value Objects

- `@dataclass(frozen=True, slots=True)` — no identity, equality is structural.
- Validate all constraints in `__post_init__` with a `DomainValidationError`.
- Place in `core/value_objects/`.

## Domain Events

- Named in **past tense**: `TranscriptionCompleted`, `RecordingStarted`.
- `@dataclass(frozen=True, slots=True)` with only primitive/serializable fields.
- Include `occurred_at: datetime` on every event.
- Place in `core/events/`.

## Repository Protocols

- Protocols in `core/interfaces/` — use domain language, return domain objects.
- Use keyword-only arguments (`*`) for all parameters.
- Never return ORM models from protocol methods.

## Ubiquitous Language

Use domain terms consistently. Forbidden inside `core/`:

- "model" → use entity, aggregate, value object
- "row" / "record" → use domain entity
- "request" / "response" → use command, query, result

## No Framework Imports

`core/` must have zero imports of `fastapi`, `sqlalchemy`, `httpx`, or any
other infrastructure framework. Use `core/interfaces/` protocols for abstraction.

## Ekko Bounded Contexts

Contexts communicate via `application/` services, never direct domain imports:

```text
Audio Processing → Transcription → AI Pipeline → Conversation
```
