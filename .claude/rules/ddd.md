---
paths:
  - "**/core/**/*.py"
---

# Domain-Driven Design Rules

Apply these tactical DDD rules to the Core layer.

## Aggregates and Entities

- Use `@dataclass(frozen=True, kw_only=True, slots=True)` for immutable domain objects.
- Enforce invariants in `__post_init__`; construction must always produce a valid object.
- Return new instances for state transitions.
- Reference other aggregates by identifier, not object graph.

## Value Objects

- Use validated scalar subclasses for scalar boundary invariants and frozen,
  keyword-only dataclasses for compound values.
- Validate every invariant at construction.
- Keep value objects identity-free with structural equality.
- Place compound domain values in `core/value_objects/` and shared scalar types
  in `core/types.py` when they cross multiple Core contracts.

## Domain Events

- Name events in past tense.
- Use `@dataclass(frozen=True, kw_only=True, slots=True)`.
- Include `occurred_at: datetime` and serializable fields only.
- Place events in `core/events/`.

## Repository and Client Ports

- Define stdlib `Protocol` contracts in `core/ports/`.
- Use domain language and keyword-only parameters.
- Return domain objects or transport-neutral port records, never ORM models.
- Infrastructure adapters implement these inward-facing contracts.

## Framework Independence

Core uses Python stdlib and other `myapp.core.*` modules only.

**Narrow exception — value-object serialization protocols:** scalar/value objects
may implement Pydantic `__get_pydantic_core_schema__` and
`__get_pydantic_json_schema__` hooks. Keep those imports inside Core scalar/value-
object modules and limit them to schema hook types. Core ports and domain behavior
MUST remain framework-independent and MUST NOT inherit from or bind generics to
`pydantic.BaseModel`.

## Ubiquitous Language

- Prefer domain terms over persistence/framework vocabulary.
- Do not expose ORM rows/models from Core.
- `*Record` names are reserved for immutable, transport-neutral port snapshots;
  they are not ORM records.
- Prefer command/query/result over request/response inside domain behavior.
