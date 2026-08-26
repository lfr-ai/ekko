---
description: Test-Driven Development workflow and test quality rules
applyTo: "**/tests/**/*.py"
---

# TDD Instructions

Apply these rules to all test code.

## The Three Laws

1. No production code without a failing test that requires it.
2. No more test code than is sufficient to fail.
3. No more production code than is sufficient to pass.

## Red-Green-Refactor

Every change follows the cycle: write failing test → minimal implementation → refactor.
Each cycle takes 1–5 minutes. Break into smaller steps if taking longer.

## Test Naming

Follow `test_{method}_{scenario}_{expected}`:

```python
# Good
def test_order_with_zero_quantity_raises_validation_error() -> None: ...
def test_service_with_valid_input_returns_result() -> None: ...

# Bad
def test_order() -> None: ...
def test_works() -> None: ...
```

## Markers (required on every test)

```python
@pytest.mark.unit         # Fast, no I/O — < 10 ms
@pytest.mark.integration  # DB, API, external services
@pytest.mark.asyncio      # Async test functions
@pytest.mark.slow         # Long-running (> 2s)
@pytest.mark.property     # Hypothesis property-based
```

## Fakes over Mocks

Use protocol-conforming fakes and factory-boy factories, not `MagicMock`:

```python
# Good — type-safe, catches interface changes
from tests.factories import OrderFactory
order = OrderFactory()

# Bad — invisible to type checker
order = MagicMock(spec=Order)
```

## Bug Fixes

Every bug fix requires a **failing regression test first**:

1. Write test that reproduces the bug (RED).
2. Fix the bug (GREEN).
3. Commit test and fix together.

## Contract Tests

Every protocol in `core/ports/` must have a contract test suite.
Wire it against all concrete implementations.

## Arrange-Act-Assert

Use blank lines to separate the three phases. No merged phases.

    # Act
    result = await service.evaluate(case)

    # Assert
    assert result.outcome == "APPROVED"
```

## Coverage Targets

| Layer | Minimum |
|-------|---------|
| Core | 90% |
| Application | 80% |
| Infrastructure | 60% |
| Presentation | 70% |

Run the project's coverage command to check.
