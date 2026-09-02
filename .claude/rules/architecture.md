---
paths:
  - "backend/src/ekko/**/*.py"
---

# Clean Architecture Boundaries

Dependencies always point inward. Never import from outer layers.

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
| `cli/` | `composition/`, `presentation/`, `config/` | entry point |

## Port / Adapter Pattern

- Ports (protocols) live in `core/ports/`
- Adapters (concrete) live in `infrastructure/` or `ai/`
- Application services depend on protocols, never concrete classes
- DI via `composition/Container` with `@cached_property`
- FastAPI `Depends()` callables in `presentation/api/dependencies.py`

## Mandatory Patterns

- `@dataclass(frozen=True, slots=True)` for all domain entities (except `Container`)
- `Final[type]` for module-level constants; `@final` for sealed classes
- Protocols in `core/ports/` for all ports
- `fastapi.status` constants, never raw HTTP integers
- Enums in `core/enums/` (split by domain)
- Domain logic in `application/services/` or `core/`, never in route handlers
