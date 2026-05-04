---
name: clean-architecture
description: Enforce Clean Architecture boundaries and dependency direction. Use when creating or moving backend modules, adding new services, or reviewing import paths.
when_to_use: When creating new files in backend/src/ekko, moving modules between layers, adding imports, creating services or repositories, reviewing dependency direction, or refactoring layer boundaries.
paths:
  - "backend/src/ekko/**/*.py"
---

# Clean Architecture

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

## Port/Adapter Pattern

- Ports (protocols) live in `core/interfaces/`
- Adapters (concrete) live in `infrastructure/` or `ai/`
- Application services depend on protocols, never concrete classes
- DI via `composition/Container` with `@cached_property`

## Violations to Catch

- `core/` importing from `application/` or `infrastructure/`
- Framework imports in `core/` (no FastAPI, SQLAlchemy)
- Business logic in route handlers (move to `application/services/`)
- Direct instantiation bypassing Container
