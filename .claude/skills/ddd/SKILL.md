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

    def __post_init__(self) -> None:
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

    def __post_init__(self) -> None:
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

    def __post_init__(self) -> None:
        if self.status == OrderStatus.COMPLETED and not self.items:
            raise ValueError("Completed orders must have items")

    def add_item(self, item: OrderItem) -> Order:
        return Order(
            order_id=self.order_id,
            customer_id=self.customer_id,
            status=self.status,
            items=self.items + (item,)
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
