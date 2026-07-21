---
description: Generate tests following Ekko project testing conventions.
---

Generate tests for the selected code following Ekko project conventions.

## Requirements

### Structure

- Place unit tests in `tests/unit/` mirroring the source path.
- Place integration tests in `tests/integration/`.
- Use `factory-boy` factories from `tests/factories/` for test data. Create new factories if needed.
- Shared fixtures go in `conftest.py` at the appropriate level.

### Markers

Apply the correct pytest markers to every test:

```python
@pytest.mark.unit           # Fast, isolated, no I/O
@pytest.mark.integration    # Database, API, external services
@pytest.mark.asyncio        # Async test functions
@pytest.mark.slow           # Long-running tests
```

### Patterns

- Use `pytest.raises` with `match=` for exception assertions.
- Use `freezegun` for time-dependent tests.
- Use `respx` for mocking `httpx` calls.
- Mock external dependencies; never call real APIs in unit tests.
- For async code, use `@pytest.mark.asyncio` and `async def test_...`.

### Naming and style

- Test names: `test_<method>_<scenario>_<expected_result>`.
- One assertion per test where practical.
- Use keyword-only args (`*` separator) for helper functions with 3+ params.
- No `Any` in test type annotations.

### Coverage targets

- Aim for at least 70% coverage on new code.
- Cover happy path, edge cases, and error conditions.
- Include property-based tests (Hypothesis) in `tests/property/` for pure functions with broad input domains.

## Output

Generate complete, runnable test files with all necessary imports.
