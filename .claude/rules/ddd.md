---
description: Domain-Driven Design quick rules for Ekko's core domain layer
paths:
  - "backend/src/ekko/core/**/*.py"
  - "backend/src/ekko/application/**/*.py"
---

# DDD Rules

## Aggregates

- `@dataclass(frozen=True, slots=True)` — always immutable
- Enforce invariants in `__post_init__` — aggregate is always valid
- Mutations return new instances, never modify in-place
- One repository protocol per aggregate root in `core/interfaces/`

## Value Objects

- `frozen=True, slots=True` — equality is structural (no identity field)
- Validate all constraints in `__post_init__` with `DomainValidationError`
- Place in `core/value_objects/`

## Domain Events

- Past-tense names: `TranscriptionCompleted`, `RecordingStarted`
- `frozen=True, slots=True` with only primitive fields + `occurred_at: datetime`
- Place in `core/events/`

## Repositories

- Protocol in `core/interfaces/` — returns domain objects, never ORM models
- Implementation in `infrastructure/db/repositories/`
- Keyword-only arguments (`*`) on all methods

## Ubiquitous Language

Never use inside `core/`: "model" (ORM), "row", "record", "payload", "request".
Use domain terms: entity, aggregate, entry, event, command, result.

## No Framework Imports

`core/` must have zero `fastapi`, `sqlalchemy`, or `httpx` imports.
Use protocols in `core/interfaces/` for abstraction.

## Context Boundaries

Bounded contexts communicate via `application/` services only.
Direct cross-context domain imports are a violation.
