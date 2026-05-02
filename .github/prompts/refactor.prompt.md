---
description: Refactor code to comply with clean architecture and Python conventions.
---

Refactor the selected code to comply with Ekko project standards.

## Apply these refactoring rules

### Architecture compliance

- Move code to the correct layer if it violates dependency direction.
- Extract business logic from route handlers into `application/services/`.
- Replace concrete adapter dependencies with protocols from `core/interfaces/`.
- Wire new services through `Container` using `@cached_property` with deferred imports.

### Type safety fixes

- Replace `Any` with `object`, generics, `Protocol`, or concrete types.
- Replace bare `dict[str, ...]` with `BaseDict` / `JSONDict`.
- Add `Final[type]` to module-level constants.
- Add `*` separator for keyword-only args on functions with 3+ parameters.
- Add `@final` decorator to classes that should not be subclassed.

### Dataclass and immutability

- Add `frozen=True, slots=True` to all `@dataclass` decorators (except `Container`).
- Convert mutable data holders to frozen dataclasses or Pydantic models.

### Logging and error handling

- Replace `print()` with `structlog` calls.
- Add exception chaining: `raise NewError(...) from original_error`.
- Add Google-style docstrings with `Raises:` only for directly raised exceptions.

### Cleanup

- Remove dead code and commented-out blocks.
- Extract magic strings into `Final[str]` constants or registry constants.
- Remove legacy shims and compatibility wrappers.

## Output

Provide the refactored code with a brief summary of changes made. If the
refactoring requires moving files across layers, list the file moves explicitly.
Ensure all existing tests still pass after the refactoring.
