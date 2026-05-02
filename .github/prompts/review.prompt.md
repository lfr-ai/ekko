---
description: Review code for clean architecture compliance, type safety, and test coverage.
---

Review the selected code (or the current diff) against the Ekko project standards.

## Check each of the following

### 1. Architecture boundaries

- Verify imports follow the dependency direction: `utils -> config -> core -> infrastructure/ai -> application -> composition -> presentation`.
- Flag any outward dependency (e.g., `core/` importing from `application/`).
- Confirm `core/` has zero framework imports (no FastAPI, SQLAlchemy, etc.).
- Ensure application services depend on protocols from `core/interfaces/`, not concrete adapters.

### 2. Type safety

- No `Any` in type annotations. Use `object`, generics, or `Protocol`.
- Dictionary types use `BaseDict` / `JSONDict`, not bare `dict[str, ...]`.
- Module-level constants use `Final[type]`.
- Functions with 3+ parameters use keyword-only args (`*` separator).

### 3. Code quality

- Dataclasses are `@dataclass(frozen=True, slots=True)` (except `Container`).
- Google-style docstrings with `Raises:` only for directly raised exceptions.
- No `print()` -- use `structlog` for logging.
- No dead code or commented-out blocks.
- Exception chaining: `raise NewError(...) from original_error`.

### 4. Test coverage

- New code has corresponding tests in the correct `tests/` subdirectory.
- Tests use `@pytest.mark.unit`, `@pytest.mark.integration`, or `@pytest.mark.asyncio` markers.
- Test data uses `factory-boy` factories from `tests/factories/`.

## Output format

For each issue found, report:
- **File and line** -- where the violation occurs.
- **Rule violated** -- which standard is broken.
- **Suggested fix** -- concrete code change to resolve it.

If no issues are found, confirm the code passes all checks.
