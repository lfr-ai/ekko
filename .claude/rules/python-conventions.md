---
paths:
  - "**/*.py"
---

# Python Conventions

- Python 3.12+ syntax: `type` aliases, `X | Y` unions, `match` statements
- Full type annotations on every function signature. No `Any` in production code.
- Use `BaseDict` / `JSONDict` instead of bare `dict[str, ...]`
- Use `*` separator when a function has 3+ parameters (keyword-only args)
- `structlog` for all logging. No `print()`.
- Google-style docstrings. `Raises:` only for exceptions raised directly in the function body.
- `raise NewError(...) from original_error` for exception chaining
- `@final` for sealed classes, `Final[type]` for constants
- `@dataclass(frozen=True, slots=True)` for all domain objects (except `Container`)
- No magic strings: extract repeated strings into `Final[str]` constants or registry constants
- Remove dead code in the same changeset. No commented-out blocks.
- `fastapi.status` constants, never raw HTTP integers
- Enums extend `ParseableEnum(StrEnum)` with `@unique` + `auto()`

## Naming

| Element | Convention |
|---------|-----------|
| Functions, methods | `snake_case` |
| Classes | `PascalCase` |
| Constants | `SCREAMING_SNAKE_CASE` with `Final[type]` |
| Type aliases | `PascalCase` |
| Protocols | `PascalCase` |
| Module files | `snake_case.py` |
