---
name: testing-conventions
description: Test quality and structure conventions. Use when adding tests, expanding coverage, or reviewing test code.
when_to_use: When writing pytest tests, creating factories, adding fixtures, using hypothesis for property tests, mocking with respx, benchmarking with pytest-benchmark, or checking coverage targets.
paths:
  - "tests/**/*.py"
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
- `pytest-benchmark` for performance

## Rules

- Test behavior, not implementation. Tests must be deterministic.
- Every bug fix gets a regression test.
- Reusable mocks in `tests/mocks/`, shared fixtures in `conftest.py`
- Minimum 70% code coverage target.
- No `unittest.TestCase` — use pytest functions.
