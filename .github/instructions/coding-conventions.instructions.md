---
description: Python coding conventions for typing, logging, and maintainability
applyTo: "**/*.py"
---

# Coding Conventions

## Stack

- Python 3.12, `uv` for packages, `ty` for type checking, `ruff` for lint/format
- `structlog` for logging (never `print()`)
- Pydantic v2 with `Annotated` + `Field`

## Hard Rules

1. No `Any` in production type annotations — use `object`, generics, or `Protocol`
2. Use `BaseDict` / `JSONDict` instead of bare `dict[str, ...]`
3. Use `*` separator for keyword-only args (3+ parameters)
4. `raise NewError(...) from original_error` for exception chaining
5. `Final[type]` for constants, `@final` for sealed classes
6. Google-style docstrings. `Raises:` only for exceptions raised directly in the body
7. No magic strings: use `Final[str]` constants or registry constants
8. No commented-out code blocks. Remove dead code in same changeset
9. `@dataclass(frozen=True, slots=True)` for all domain objects (except `Container`)
10. `fastapi.status` constants, never raw HTTP integers
11. Enums extend `ParseableEnum(StrEnum)` with `@unique` + `auto()`

## Naming

| Element | Convention |
|---------|-----------|
| Functions, methods | `snake_case` |
| Classes | `PascalCase` |
| Constants | `SCREAMING_SNAKE_CASE` with `Final[type]` |
| Type aliases | `PascalCase` |
| Protocols | `PascalCase` |
| Module files | `snake_case.py` |
