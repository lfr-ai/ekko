---
name: python-conventions
description: Python coding standards for typing, logging, and maintainability. Use when writing or reviewing Python code.
when_to_use: When writing new Python functions, classes, or modules. When reviewing type annotations, docstrings, logging, exception handling, dataclass definitions, or constant declarations.
paths:
  - "**/*.py"
---

# Python Conventions

## Stack

- Python 3.12, `uv` for packages, `ty` for type checking, `ruff` for lint/format
- `structlog` for logging (never `print()`)
- Pydantic v2 with `Annotated` + `Field`
- `@dataclass(frozen=True, slots=True)` for all domain objects

## Hard Rules

1. No `Any` in production type annotations
2. Use `BaseDict` / `JSONDict` instead of bare `dict[str, ...]`
3. Use `*` separator for keyword-only args (3+ parameters)
4. `raise NewError(...) from original_error` for exception chaining
5. `Final[type]` for constants, `@final` for sealed classes
6. Google-style docstrings. `Raises:` only for exceptions raised directly in the body.
7. No magic strings: use `Final[str]` constants or registry constants
8. No commented-out code blocks. Remove dead code in same changeset.
