---
paths:
  - "tests/**/*.py"
---

# Testing Conventions

- Use `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.asyncio`, `@pytest.mark.slow`
- `factory-boy` for test data (`tests/factories/`)
- `hypothesis` for property-based tests (`tests/property/`)
- `freezegun` for time-dependent tests
- `respx` for mocking httpx calls
- `pytest-benchmark` for performance assertions
- Reusable mocks in `tests/mocks/`, shared fixtures in `tests/fixtures/` or `conftest.py`
- Test behavior, not implementation. Tests must be deterministic.
- Every bug fix gets a regression test.
- Minimum 70% code coverage target.
- No `unittest.TestCase` — use pytest functions.
- Test naming: `test_{method}_{scenario}_{expected}`
- Arrange-Act-Assert structure in all tests.
