---
name: ddd
description: "Domain-Driven Design tactical patterns for the domain layer. Use when designing entities, value objects, aggregates, or reviewing domain model compliance."
---

# Domain-Driven Design (DDD) Skill

Tactical DDD patterns for the domain layer (`core/`).

## When to Use This Skill

- Designing new domain concepts (entities, value objects, aggregates)
- Reviewing domain model for DDD compliance
- Identifying aggregate boundaries
- Extracting value objects from primitives
- Modeling domain events
- Creating repository protocols

## DDD Tactical Patterns

### 1. Entities

**Definition**: Objects with identity that persists over time.

**Implementation**:
```python
from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True, slots=True)
class Order:
    """Order entity with lifecycle."""

    order_id: str  # Identity
    customer_id: str
    status: OrderStatus
    created_at: datetime

    def __post_init__(self):  # noqa: ANN204
        if not self.order_id:
            raise ValueError("Order must have an ID")
```

**Checklist**:
- [ ] Has clear identity field
- [ ] `@dataclass(frozen=True)` for immutability
- [ ] `__post_init__` validates invariants
- [ ] Located in `core/entities/`

### 2. Value Objects

**Definition**: Objects without identity — equality is structural.

**Implementation**:
```python
from __future__ import annotations


@dataclass(frozen=True, kw_only=True, slots=True)
class Money:
    """Money value object with currency."""

    amount: Decimal
    currency: str

    def __post_init__(self):  # noqa: ANN204
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        if len(self.currency) != 3:
            raise ValueError("Currency must be ISO 4217 code")

    def add(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)
```

**Checklist**:
- [ ] `@dataclass(frozen=True, kw_only=True, slots=True)`
- [ ] No identity field
- [ ] `__post_init__` validates constraints
- [ ] Located in `core/value_objects/`
- [ ] Operations return new instances
- [ ] Generated `__repr__` is retained unless a field contains sensitive or large data
- [ ] Sensitive or large dataclass fields use `field(repr=False)`; scalar personal identifiers use a masked custom `__repr__`

**When to Extract Value Objects**:
- Primitive obsession (strings/ints representing domain concepts)
- Cohesive group of attributes (address: street, city, postal_code)
- Complex validation rules
- Reusable across entities

### 3. Aggregates

**Definition**: Cluster of entities and value objects treated as a single unit.

```python
from __future__ import annotations


@dataclass(frozen=True, kw_only=True, slots=True)
class Order:
    """Order aggregate root."""

    order_id: str
    customer_id: str
    status: OrderStatus
    items: tuple[OrderItem, ...]

    def __post_init__(self):  # noqa: ANN204
        if self.status == OrderStatus.COMPLETED and not self.items:
            raise ValueError("Completed orders must have items")

    def add_item(self, item: OrderItem) -> Order:
        return Order(
            order_id=self.order_id,
            customer_id=self.customer_id,
            status=self.status,
            items=self.items + (item,),
        )
```

**Checklist**:
- [ ] Clear aggregate root identified
- [ ] Owns child entities/value objects
- [ ] All invariants enforced
- [ ] References other aggregates by ID
- [ ] Mutations return new instances
- [ ] One repository per aggregate root

### 4. Domain Events

**Definition**: Something significant that happened in the domain.

```python
@dataclass(frozen=True, kw_only=True, slots=True)
class OrderPlaced:
    """Domain event: order was placed."""

    order_id: str
    customer_id: str
    total: Decimal
    occurred_at: datetime
```

**Checklist**:
- [ ] Named in past tense
- [ ] `@dataclass(frozen=True, kw_only=True, slots=True)`
- [ ] `occurred_at: datetime` field
- [ ] Only primitive/serializable fields
- [ ] Located in `core/events/`

### 5. Repository Protocols

```python
class OrderRepository(Protocol):
    async def get(self, *, order_id: str) -> Order | None: ...
    async def save(self, *, order: Order) -> None: ...
    async def find_by_customer(self, *, customer_id: str) -> list[Order]: ...
```

**Checklist**:
- [ ] Protocol in `core/ports/`
- [ ] Returns domain objects (not ORM)
- [ ] Keyword-only arguments
- [ ] Domain language in method names
- [ ] One repository per aggregate root

A repository/client/store port is the codebase's default polymorphism
mechanism (structural, via `Protocol`) — see `python-conventions`'
[`references/polymorphism-patterns.md`](../python-conventions/references/polymorphism-patterns.md)
for the Protocol-vs-ABC decision and the `@override` Liskov check.

## Common DDD Violations

| Violation | Fix |
|-----------|-----|
| ORM model in core | Use domain entity, add mapper |
| Anemic domain | Add behavior and invariants to entities |
| Repository returns ORM | Return domain objects |
| Framework imports in core | Use stdlib protocols in `core/ports/` |
| Direct aggregate references | Use IDs instead |
| Large aggregates | Split along consistency boundaries |

## Ubiquitous Language

Inside `core/`, use domain terms only:

| Forbidden | Domain Alternative |
|-----------|--------------------|
| "model" (ORM) | entity, aggregate, value object |
| "row" / "record" | entity, domain-specific term |
| "request" / "response" | command, query, result |
| "data" / "payload" | domain-specific term |

## Framework Independence

- Core uses stdlib and other `myapp.core.*` modules only.
- Narrow exception: scalar/value objects may implement Pydantic
    `__get_pydantic_core_schema__` / `__get_pydantic_json_schema__` hooks as
    boundary serialization protocols.
- Keep that exception inside Core scalar/value-object modules and limit imports
    to schema hook types. Core ports must not inherit from or bind generics to
    `pydantic.BaseModel`.
- Model external behavior with stdlib `Protocol` contracts in `core/ports/`.

## Templates and references

- [`assets/entity.py.template`](assets/entity.py.template),
  [`assets/value_object.py.template`](assets/value_object.py.template),
  [`assets/domain_event.py.template`](assets/domain_event.py.template),
  [`assets/repository_protocol.py.template`](assets/repository_protocol.py.template),
  [`assets/domain_exceptions.py.template`](assets/domain_exceptions.py.template)
  — copy-and-rename starting points for each pattern above, including the
  domain error hierarchy: a `DomainError` base every first-party exception
  inherits, one named `@final` `ReplaceMeNotFoundError(DomainError)` per
  distinct not-found case (never a generic parameterized `NotFoundError`, and
  never also inheriting stdlib `LookupError`), and the port-level
  shape (each `*ClientPort` gets its OWN distinctly-named result exception —
  e.g. `ReplaceMeUnusableResultError` — never one generic type reused across
  multiple, unrelated client ports; a `*RepositoryPort`'s
  `PersistenceUnavailableError`, each `DomainError` in a sibling
  `exceptions.py` next to that port). Other invariant violations raise
  stdlib `ValueError`/`TypeError` directly, so existing `except
  ValueError`-style handling keeps working unless a call site needs a more
  specific `except`. Pair with `backend-structure`'s
  `assets/exception_handlers.py.template`, which maps each `*ClientPort`
  exception to 502 and `PersistenceUnavailableError` to 503.
- **Adapter boundary translation**: an infrastructure adapter must translate a
  third-party library's response-shape failure (a missing field, malformed
  encoding, unparsable body — the call succeeded but what came back is
  unusable) into its port's `DomainError` subclass, never let the raw
  library exception (`KeyError`, `binascii.Error`, a provider SDK's own
  error type) leak past the adapter. This keeps every caller's `except`
  vocabulary limited to first-party types. Pure transport failures (a
  timed-out connection, a non-2xx `raise_for_status()`) are a different
  concern already handled by `infrastructure/retry_policies.py`'s retry
  policies — leave those to propagate after retries are exhausted rather
  than wrapping them too.
- [`assets/service_port_protocol.py.template`](assets/service_port_protocol.py.template)
  — a non-repository port (a client, store, or metrics recorder): one or a
  few cohesive methods instead of the CRUD shape `repository_protocol.py.template`
  models. Use whichever of the two matches the capability being ported.
- [`assets/service_adapter.py.template`](assets/service_adapter.py.template) —
  the adapter side of `service_port_protocol.py.template`: explicitly
  subclasses its port and decorates every method `@override`, built via
  `from_config` (see the `configuration` skill). The repository side has its
  own adapter template in the `database-migrations` skill's
  `assets/repository_impl.py.template`.
- [`references/aggregate-boundary-checklist.md`](references/aggregate-boundary-checklist.md)
  — how to size an aggregate, enforce one-repository-per-root, and wire
  cross-aggregate consistency through domain events.

## Enforcement

- [`scripts/check_port_adapter_binding.py`](scripts/check_port_adapter_binding.py)
  — read-only AST check for the port/adapter inheritance contract: flags a
  `*Port`-named class that does not subclass `Protocol`, and an adapter
  (subclasses a `*Port` base) with a method missing `@override`. ty
  type-checks `@override` when present but has no rule requiring it to be
  present at all — this closes that gap. Run:
  `uv run python scripts/check_port_adapter_binding.py src/<pkg>`.
