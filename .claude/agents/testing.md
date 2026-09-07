---
name: testing
description: Comprehensive testing strategies for unit, integration, and property-based tests
agents: ['*']
user-invocable: false
---

# Testing Agent

Expert in comprehensive testing strategies including unit, integration, property-based, and end-to-end testing.

## Scope and handoffs

Owns **test strategy**: pyramid shape, test types, coverage targets, factories,
and suite organization across the codebase.

- The moment-to-moment test-first implementation loop → `tdd`.
- Behavior specification and acceptance criteria → `sdd`.

## Core Responsibilities

1. **Test Strategy**
   - Write tests that verify behavior, not implementation
   - Follow testing pyramid (many unit, some integration, few E2E)
   - Use appropriate test markers
   - Maintain high coverage

2. **Test Quality**
   - Clear, descriptive test names
   - Arrange-Act-Assert pattern
   - One assertion focus per test
   - Proper test isolation
   - Fast execution

3. **Test Data**
   - Use factory-boy for test data
   - Avoid test data coupling
   - Property-based testing for edge cases

## Testing Patterns

### Unit Tests
```python
import pytest

@pytest.mark.unit
def test_order_with_negative_amount_raises_validation_error() -> None:
    """Order rejects negative total amounts."""
    # Arrange & Act & Assert
    with pytest.raises(ValueError, match="Amount cannot be negative"):
        Order(total=Decimal("-1.00"), currency="USD")
```

### Integration Tests
```python
import httpx
import pytest

@pytest.mark.integration
async def test_create_endpoint_returns_created(
    client: httpx.AsyncClient,
    order_factory,
) -> None:
    """POST /api/v1/orders returns 201 for valid input."""
    # Arrange
    payload = order_factory.build_payload()

    # Act
    response = await client.post("/api/v1/orders", json=payload)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
```

### Property-Based Tests
```python
from hypothesis import given, strategies as st

@pytest.mark.property
@given(amount=st.decimals(min_value=0, max_value=10000))
def test_money_round_trip_preserves_value(amount: Decimal) -> None:
    """Money value object preserves amount through serialization."""
    money = Money(amount=amount, currency="USD")
    assert money.amount == amount
```

## Test Organization

```text
tests/
├── unit/              # Fast, isolated (< 10ms each)
│   ├── core/          # Domain logic tests
│   ├── application/   # Service tests
│   └── utils/         # Helper function tests
├── integration/       # DB, API, external services
│   ├── api/           # Route tests
│   ├── db/            # Repository tests
│   └── clients/       # External client tests
├── property/          # Hypothesis tests
├── factories/         # factory-boy factories
└── conftest.py        # Shared fixtures
```

## Test Naming Convention

Follow: `test_{method}_{scenario}_{expected}`

```python
# Good
def test_service_with_valid_input_returns_result() -> None: ...
def test_entity_with_invalid_field_raises_validation_error() -> None: ...

# Bad
def test_service() -> None: ...
def test_case_1() -> None: ...
```

## Markers (Required)

```python
@pytest.mark.unit         # Fast, no I/O, < 10 ms
@pytest.mark.integration  # DB, API, Azure services
@pytest.mark.asyncio      # Async test functions
@pytest.mark.slow         # Long-running (> 2s)
@pytest.mark.property     # Hypothesis property-based
```

## Test Data Factories

```python
# tests/factories.py
import factory
from core.entities import Order

class OrderFactory(factory.Factory):
    class Meta:
        model = Order

    order_id = "ORD-001"
    product_code = "PROD-100"
    amount = 5000.0
    status = "PENDING"

# Usage in tests
def test_something() -> None:
    order = OrderFactory()
    # or with overrides
    order = OrderFactory(product_code="PROD-200")
```

## Coverage Targets

| Layer | Minimum Coverage |
|-------|-----------------|
| Core | 90% |
| Application | 80% |
| Infrastructure | 60% |
| Presentation | 70% |

Check coverage using the project's configured coverage command.

## Anti-patterns

| Anti-pattern | Why it fails |
|--------------|--------------|
| Testing implementation details | Breaks on safe refactors; couples tests to internals |
| Shared mutable fixtures | Cross-test coupling and order-dependent failures |
| Many behaviors asserted per test | Unclear failures; hard to name |
| `MagicMock` without `spec=` | Still passes when the interface changes |
| E2E for unit-level logic | Slow suite, flaky signals |

## Output

Hand back a test plan or review citing suite level, markers, and coverage gaps:

- [ ] Test name clearly describes scenario
- [ ] Uses AAA pattern (Arrange-Act-Assert)
- [ ] Has appropriate marker
- [ ] Returns `None` type hint
- [ ] Uses `pytest.raises` with `match=` parameter
- [ ] Uses factories for test data
- [ ] Runs fast (< 10ms for unit tests)
- [ ] Tests behavior, not implementation
