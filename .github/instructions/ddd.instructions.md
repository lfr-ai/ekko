---
description: Domain-Driven Design patterns for the domain layer
applyTo: "src/**/core/**/*.py"
---

# Domain-Driven Design Instructions

Apply DDD tactical patterns to all code in the core layer. Templates, worked
examples, and the port/adapter enforcement script live in the `ddd` skill
(`.agents/skills/ddd/SKILL.md`) — pull it up for deep patterns.

## Rules

- Aggregates and value objects: `@dataclass(frozen=True, kw_only=True, slots=True)`;
  invariants enforced in `__post_init__`; mutations return new instances.
  One repository per aggregate root; aggregates reference each other by ID only.
- Domain events: named in past tense (`OrderPlaced`), only primitive/serializable
  fields, always include `occurred_at: datetime`, placed in `core/events/`.
- Repository protocols live in `core/ports/`, use domain language, return
  domain objects (never ORM models), keyword-only parameters.
- Place compound value objects in `core/value_objects/`; shared scalar types
  that cross multiple Core contracts go in `core/types.py`.
- Keep the dataclass-generated `__repr__` by default. Mark sensitive or large
  payload fields with `field(repr=False)`; scalar national identifiers require
  an explicit masked, non-reconstructible `__repr__`.

## Ubiquitous Language

Use domain terms consistently. Forbidden in `core/`:

- "model" → use entity, aggregate, value object
- "row"/"record" → use domain entity
- "request"/"response" → use command, query, DTO
- "data"/"payload" → use domain-specific term

`*Record` names are reserved for immutable, transport-neutral port snapshots —
they are not ORM records.

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
