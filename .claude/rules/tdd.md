---
description: Test-Driven Development rules for all test files
paths:
  - "tests/**/*.py"
---

# TDD Rules

## The Three Laws

1. No production code without a failing test that requires it.
2. No more test code than is sufficient to fail.
3. No more production code than is sufficient to pass.

## Test Naming

`test_{method}_{scenario}_{expected}` — always descriptive, always specific.

## Markers (required on every test)

- `@pytest.mark.unit` — fast, no I/O, < 10 ms
- `@pytest.mark.integration` — DB, API, external services
- `@pytest.mark.asyncio` — async test functions
- `@pytest.mark.slow` — > 2 seconds

## Fakes over Mocks

Protocol-conforming fakes in `tests/mocks/`. No `MagicMock` on domain interfaces.

## Bug Fixes

Every bug fix starts with a **failing regression test**.
Test + fix committed together in the same commit.

## Contract Tests

Every `core/interfaces/` protocol has a contract test in `tests/unit/core/interfaces/`.

## Arrange-Act-Assert

Three phases separated by blank lines. No merged phases.

## Coverage

Minimum 70%. Run `task test:coverage` before marking a task complete.
