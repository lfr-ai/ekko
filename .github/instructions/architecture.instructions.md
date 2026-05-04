---
description: Clean Architecture boundaries and dependency direction for Python source files
applyTo: "backend/src/ekko/**/*.py"
---

# Architecture Instructions

Dependencies always flow **inward**. Outer layers depend on inner layers, never the reverse.

```text
utils -> config -> core -> infrastructure/ai -> application -> composition -> presentation
```

## Import Rules

| Layer | May Import From | NEVER From |
|-------|----------------|------------|
| `utils/` | stdlib ONLY | ALL other project layers |
| `config/` | `utils/`, external libs | `presentation/`, `application/`, `core/` |
| `core/` | `utils/`, `config/` | `presentation/`, `application/`, `infrastructure/` |
| `infrastructure/` | `core/`, `config/`, `utils/`, external libs | `presentation/`, `application/` |
| `ai/` | `core/`, `config/`, `utils/` | `presentation/`, `application/`, `infrastructure/` |
| `application/` | `core/`, `infrastructure/`, `ai/`, `config/`, `utils/` | `presentation/` |
| `presentation/` | `application/`, `core/`, `config/`, `utils/` | top layer |

## Port / Adapter Pattern

- Ports (protocols) live in `core/interfaces/`
- Adapters (concrete) live in `infrastructure/` or `ai/`
- Application services depend on protocols, never concrete classes
- DI via `composition/Container` with `@cached_property`
- FastAPI `Depends()` callables in `presentation/api/dependencies.py`

## Mandatory Patterns

- `@dataclass(frozen=True, slots=True)` for all domain entities (except `Container`)
- `Final[type]` for module-level constants; `@final` for sealed classes
- `fastapi.status` constants, never raw HTTP integers
- Enums in `core/enums/` (split by domain). Import via `from ekko.core.enums import X`
- Concurrency primitives in `infrastructure/concurrency/`
- Domain logic in `application/services/` or `core/`, never in route handlers
