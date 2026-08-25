---
name: testing-conventions
description: 'Enforces test structure, markers, factory-based data, and coverage thresholds. Use when adding tests, expanding regression suites, or verifying test quality.'
---

# Testing Conventions Skill

## Test Structure

```text
tests/
├── unit/
│   ├── conftest.py          # Shared fixtures
│   ├── core/                # Domain logic tests
│   ├── application/         # Service layer tests
│   └── utils/               # Utility function tests
├── integration/
│   ├── api/                 # API endpoint tests
│   ├── db/                  # Repository tests
│   └── clients/             # External client tests
├── property/                # Hypothesis property-based tests
├── factories/               # factory-boy factories
└── conftest.py              # Shared fixtures
```

## Naming Conventions

| Element | Pattern | Example |
|---------|---------|--------|
| Test file | `test_{module}.py` | `test_order_service.py` |
| Test class | `Test{ClassName}` | `TestOrderService` |
| Test method | `test_{method}_{scenario}_{expected}` | `test_process_order_empty_input_raises_error` |
| Fixture | `{noun}_fixture` or `sample_{noun}` | `sample_order` |

## Test Template

```python
"Tests for {module_name}."

import pytest
from hypothesis import given, strategies as st


class TestSymbol:
    "Tests for Symbol."

    def test_method_happy_path(self) -> None:
        "Method returns expected result for valid input."
        # Arrange
        input_data = ...

        # Act
        result = Symbol().method(input_data)

        # Assert
        assert result == expected

    def test_method_empty_input(self) -> None:
        "Method handles empty input gracefully."
        with pytest.raises(ValueError, match="cannot be empty"):
            Symbol().method("")

    @pytest.mark.parametrize(
        "input_val, expected",
        [
            (1, "one"),
            (2, "two"),
            (3, "three"),
        ],
    )
    def test_method_parametrized(
        self, input_val: int, expected: str
    ) -> None:
        "Method maps input to correct output."
        assert Symbol().method(input_val) == expected

    @given(st.integers(min_value=0, max_value=100))
    def test_method_property(self, value: int) -> None:
        "Method output is always non-negative."
        result = Symbol().method(value)
        assert result >= 0
```

## Fixture Patterns

### Factory Fixtures (preferred)

```python
@pytest.fixture
def order_factory():
    "Create test orders with sensible defaults."
    def _factory(**overrides) -> dict[str, object]:
        defaults = {
            "id": 1,
            "product": "Test Product",
            "status": "pending",
        }
        return {**defaults, **overrides}
    return _factory
```

## Rules

- All test functions MUST have `-> None` return type
- Use `pytest.raises(ExcType, match="pattern")` — always include `match`
- Use `pytest.mark.parametrize` for data-driven tests
- Use `monkeypatch` for environment variables (never `os.environ` directly)
- Use `tmp_path` for filesystem tests
- Mark slow tests: `@pytest.mark.slow`
- Never test private methods (underscore-prefixed)
- Never use `time.sleep()` in tests
- Never use mutable defaults in fixtures

## Anti-Patterns

| Anti-Pattern | Correct Pattern |
|-------------|----------------|
| Testing private methods | Test through public API |
| `time.sleep()` in tests | Use `pytest-timeout` or mocks |
| Shared mutable state | Factory fixtures |
| `assert True` / `assert not False` | Assert specific values |
| Exact float comparison | `pytest.approx()` |
| Ignoring test warnings | Fix root cause |
