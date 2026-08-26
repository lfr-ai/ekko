---
description: Clean Architecture boundaries and dependency direction for Python source files
applyTo: "backend/src/ekko/**/*.py"
---

# Architecture Instructions

Dependencies always flow **inward**. Outer layers depend on inner layers, never the reverse.
Enforced by import-linter contracts in `backend/pyproject.toml`; run `task architecture`.

```text
config -> core -> {ai | infrastructure} -> application -> presentation -> composition -> cli
```

## Import Rules

| Layer | May Import From | NEVER From |
|-------|----------------|------------|
| `config/` | external libs, stdlib | `core/`, `infrastructure/`, `ai/`, `application/`, `presentation/` |
| `core/` | `config/`, stdlib (+ Pydantic hooks) | `infrastructure/`, `ai/`, `application/`, `presentation/` |
| `infrastructure/` | `core/`, `config/`, external libs | `ai/`, `application/`, `presentation/` |
| `ai/` | `core/`, `config/` | `infrastructure/`, `application/`, `presentation/` |
| `application/` | `core/`, `infrastructure/`, `ai/`, `config/` | `presentation/` |
| `presentation/` | `application/`, `core/`, `config/` | `infrastructure/`, `ai/`, `composition/` |
| `composition/` | all layers (DI wiring) | — |
| `cli/` | `composition/`, `presentation/`, `config/` | (entrypoint) |

## Port / Adapter Pattern

- Ports (protocols) live in `core/ports/`
- Adapters (concrete) live in `infrastructure/` or `ai/`
- Application services depend on protocols, never concrete classes
- `ai` and `infrastructure` are sibling verticals: neither imports the other
- DI via `composition/Container` with `@cached_property`
- FastAPI `Depends()` callables in `presentation/api/dependencies.py`

## Mandatory Patterns

- `@dataclass(frozen=True, slots=True)` for all domain entities (except `Container`)
- `Final[type]` for module-level constants; `@final` for sealed classes
- `fastapi.status` constants, never raw HTTP integers
- Enums in `core/enums/` (split by domain). Import via `from ekko.core.enums import X`
- Concurrency primitives in `infrastructure/concurrency/`
- Domain logic in `application/services/` or `core/`, never in route handlers
