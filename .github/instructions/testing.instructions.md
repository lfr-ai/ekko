---
description: Test structure, markers, libraries, and quality conventions
applyTo: "tests/**/*.py"
---

# Testing Conventions

## Markers

- `@pytest.mark.unit` — fast, isolated, no I/O
- `@pytest.mark.integration` — database, API, external services
- `@pytest.mark.asyncio` — async test functions
- `@pytest.mark.slow` — long-running tests

## Libraries

- `factory-boy` for test data (`tests/factories/`)
- `hypothesis` for property-based tests (`tests/property/`)
- `freezegun` for time-dependent tests
- `respx` for mocking httpx calls
- `pytest-benchmark` for performance assertions

## Rules

- Test behavior, not implementation. Tests must be deterministic.
- Every bug fix gets a regression test.
- Reusable mocks in `tests/mocks/`, shared fixtures in `conftest.py`
- Minimum 70% code coverage target.
- No `unittest.TestCase` — use pytest functions.
- Test naming: `test_{method}_{scenario}_{expected}`
- Arrange-Act-Assert structure in all tests.
