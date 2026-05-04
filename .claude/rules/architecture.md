---
paths:
  - "backend/src/ekko/**/*.py"
---

# Clean Architecture Boundaries

Dependencies always point inward. Never import from outer layers.

## Import Rules

| Layer | May Import From | NEVER From |
|-------|----------------|------------|
| `utils/` | stdlib ONLY | ALL other project layers |
| `config/` | `utils/`, external libs | `presentation/`, `application/`, `core/` |
| `core/` | `utils/`, `config/` | `infrastructure/`, `application/`, `presentation/` |
| `infrastructure/` | `core/`, `config/`, `utils/` | `application/`, `presentation/` |
| `ai/` | `core/`, `config/`, `utils/` | `infrastructure/`, `application/`, `presentation/` |
| `application/` | `core/`, `infrastructure/`, `ai/`, `config/`, `utils/` | `presentation/` |
| `composition/` | ALL inner layers | `presentation/` (except wiring) |
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
- Protocols in `core/interfaces/` for all ports
- `fastapi.status` constants, never raw HTTP integers
- Enums in `core/enums/` (split by domain)
- Domain logic in `application/services/` or `core/`, never in route handlers
