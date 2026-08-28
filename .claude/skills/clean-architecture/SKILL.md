---
name: clean-architecture
description: 'Enforces Clean Architecture boundaries and the Dependency Rule. Use when creating or moving modules, reviewing imports, or validating layer compliance.'
---

# Clean Architecture Skill

## Layer Hierarchy

```text
core/ → application/ → infrastructure/ → composition/ → presentation/ → main
```

Inner layers have ZERO knowledge of outer layers.
Outer layers depend on inner layers through imports.

> **Layer names below are the Python backend convention.** The frontend applies
> the same Dependency Rule with its own layers (`domain → application →
> infrastructure → presentation`, plus `router`/`lib`); see the
> `frontend-structure` skill for the React/TypeScript mapping.

## Dependency Rule

The fundamental invariant: **source-code dependencies always point inward**.

| Layer | Responsibility | Dependencies |
|-------|---------------|-------------|
| `core/` | Entities, value objects, interfaces (ports), exceptions, domain enums | stdlib; narrow Pydantic serialization hooks on value objects only |
| `application/` | DTOs, handlers, services, mappers | `core/`, `configs/` |
| `infrastructure/` | Persistence, clients, external adapters | `core/`, `configs/`, external libs; never `application/` |
| `composition/` | DI container (wiring layer) | ALL layers |
| `presentation/` | Routes, middleware, API schemas | `application/`, selected `core/` contracts/values, `configs/`; never `composition/` |

## Boundary Rules

### Core Layer
- ZERO external imports except the serialization hooks described below
- Exception: scalar/value objects may implement Pydantic core/JSON schema dunder
	hooks as serialization protocols. Core ports and domain behavior remain
	framework-independent.
- Entities: immutable dataclasses with `frozen=True`
- Value objects: `@dataclass(frozen=True, kw_only=True, slots=True)`
- Interfaces: `Protocol` classes defining ports for adapters
- Exceptions: Domain-specific exceptions

### Application Layer
- Orchestrates use cases using core entities and protocols
- Never directly imports infrastructure
- Returns DTOs at boundaries

### Infrastructure Layer
- Implements core protocols (adapters)
- ORM models, repository implementations, external clients
- Maps between ORM and domain objects
- Does not import application DTOs or enums; use Core contracts or adapter-local
	wire constants.

### Composition Layer
- Wires all dependencies together
- DI container resolves implementations
- Only layer allowed to import everything

### Presentation Layer
- Thin controllers contain transport mapping only
- Delegate orchestration and policy to application services
- Behavior-free CRUD may call inward Core repository ports directly; do not add
	one-method application wrappers that merely repeat a port call
- Obtain runtime dependencies through structural request-state contracts; never
	import the concrete composition container
- No business logic in routes
- Input validation and serialization only

## Adding a New Layer Component

1. Create module in the correct layer directory
2. Import only from allowed layers (see table above)
3. Add type hints, docstrings, and constants
4. Wire dependencies through DI if needed
5. Create tests in `tests/unit/` mirroring source structure

## Common Violations

| Violation | Example | Fix |
|-----------|---------|-----|
| Outward import | `core/` imports from `infrastructure/` | Use protocol in `core/ports/` |
| Circular import | A ↔ B | Extract shared interface to lower layer |
| Hardcoded DI | `service = MyService()` in route | Use dependency injection |
| Business logic in route | Complex logic in handler | Move to `application/services/` |
| ORM model in domain | SQLAlchemy model in `core/` | Create domain entity + mapper |
