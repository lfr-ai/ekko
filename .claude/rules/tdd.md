---
description: Test-Driven Development rules for all test files
paths:
  - "**/tests/**/*.py"
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
- `@pytest.mark.property` — Hypothesis property-based tests

## Fakes over Mocks

Use factory-boy factories. No `MagicMock` on domain objects.

## Bug Fixes

Every bug fix starts with a **failing regression test**.
Test + fix committed together in the same commit.

## Contract Tests

Every `core/ports/` protocol has a contract test suite.
Wire it against all concrete implementations.

## Arrange-Act-Assert

Three phases separated by blank lines. No merged phases.

## Coverage

| Layer | Minimum |
|-------|---------|
| Core | 90% |
| Application | 80% |
| Infrastructure | 60% |
| Presentation | 70% |
