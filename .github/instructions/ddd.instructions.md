---
description: Domain-Driven Design patterns for the domain layer
applyTo: "**/core/**/*.py"
---

# Domain-Driven Design Instructions

Apply DDD tactical patterns to all code in the core layer.

## Aggregates

- `@dataclass(frozen=True, kw_only=True, slots=True)` on all aggregate roots
- All invariants enforced in `__post_init__` — aggregate is always valid after construction
- Mutations return **new instances** (functional style)
- One repository per aggregate root (protocol in `core/ports/`)
- No direct references between aggregates — use IDs only

## Value Objects

- `@dataclass(frozen=True, kw_only=True, slots=True)` — no identity, structural equality
- Validate all constraints in `__post_init__` with domain exception
- Place in `core/value_objects/`
- Self-validating on construction

## Domain Events

- Named in **past tense**: `OrderPlaced`, `PaymentProcessed`
- `@dataclass(frozen=True, kw_only=True, slots=True)` with only primitive fields
- Include `occurred_at: datetime` on every event
- Place in `core/events/`

## Repository Protocols

- Protocols in `core/ports/` using domain language
- Return domain objects, **never ORM models**
- Keyword-only arguments (`*`) for all parameters
- Methods express domain queries

## Ubiquitous Language

Use domain terms consistently. Forbidden in `core/`:

- "model" → use entity, aggregate, value object
- "row"/"record" → use domain entity
- "request"/"response" → use command, query, DTO
- "data"/"payload" → use domain-specific term

## Framework Independence

`core/` must have **ZERO imports** from application frameworks (FastAPI, Django,
Flask) or infrastructure libraries (SQLAlchemy, httpx, boto3).

**Allowed exception — serialization protocols**: Value objects MAY implement
Pydantic's `__get_pydantic_core_schema__` / `__get_pydantic_json_schema__`
dunder methods. These are **serialization protocol contracts** — analogous to
`__repr__`, `__format__`, or `__json__` — that declare how to serialize the type
at system boundaries without coupling domain logic to the framework.

Keep this exception inside Core scalar/value-object modules and limit imports to
schema hook types. Core ports MUST NOT inherit from or bind generics to
`pydantic.BaseModel`.

Use stdlib `Protocol` contracts in `core/ports/` for all other abstraction needs.
