---
name: tdd
description: "Test-Driven Development Red-Green-Refactor methodology. Use when implementing features test-first, fixing bugs with regression tests, or refactoring with test safety nets."
---

# Test-Driven Development (TDD) Skill

Strict Red-Green-Refactor methodology for building reliable software.

## When to Use This Skill

- Implementing new features with test-first approach
- Fixing bugs with regression tests
- Refactoring with test safety net
- Writing contract tests for protocol interfaces
- Achieving coverage targets per architectural layer

## The Three Laws

1. No production code without a failing test that requires it.
2. No more test code than is sufficient to fail.
3. No more production code than is sufficient to pass.

## TDD Cycle

```text
RED → GREEN → REFACTOR → (repeat)
```

Each cycle should take 1-5 minutes. If it takes longer, break into smaller steps.

### RED Phase
Write a test that:
- Describes the desired behavior in its name
- Uses concrete values (not vague inputs)
- Fails for the RIGHT reason (compilation error or assertion failure)

```python
@pytest.mark.unit
def test_money_with_negative_amount_raises_validation_error() -> None:
    "Money value object rejects negative amounts."
    with pytest.raises(ValueError, match="Amount cannot be negative"):
        Money(amount=Decimal("-1.00"), currency="USD")
```

### GREEN Phase
Write the MINIMAL code to pass:
- Don't over-engineer
- Don't add features not required by the test
- It's OK to hard-code if only one test exists

### REFACTOR Phase
Improve structure without changing behavior:
- Extract duplication
- Rename for clarity
- Simplify logic
- ALL tests must remain green

## Test Quality Standards

### Naming
Follow `test_{method}_{scenario}_{expected}`:
```python
def test_order_with_zero_quantity_raises_validation_error() -> None: ...
def test_repository_with_unknown_id_returns_none() -> None: ...
```

### Structure (AAA)
```python
def test_service_processes_valid_input() -> None:
    # Arrange
    entity = EntityFactory()
    service = ServiceUnderTest()

    # Act
    result = service.process(entity)

    # Assert
    assert result.status == ExpectedStatus.COMPLETED
```

### Markers (required)
- `@pytest.mark.unit` — fast, no I/O, < 10 ms
- `@pytest.mark.integration` — DB, API, external services
- `@pytest.mark.property` — Hypothesis property-based tests

### Fakes over Mocks
Use factory-boy factories. No `MagicMock` on domain objects.

## Coverage Targets

| Layer | Minimum |
|-------|---------|
| Core | 90% |
| Application | 80% |
| Infrastructure | 60% |
| Presentation | 70% |

## Bug Fix Protocol

1. Write failing regression test (RED)
2. Fix the bug (GREEN)
3. Commit test + fix together
4. Never fix a bug without a test

## Checklist

- [ ] Failing test written BEFORE implementation
- [ ] Test name describes behavior, not implementation
- [ ] `pytest.raises` uses `match=` parameter
- [ ] AAA phases separated by blank lines
- [ ] Factory-boy for test data (no MagicMock on domain)
- [ ] All tests pass after refactoring
- [ ] Coverage targets met
