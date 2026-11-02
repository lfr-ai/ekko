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

Group repo-hygiene/meta tests (architecture guards, agent-config parity, dependency-audit
contracts — tests *of the codebase itself*, not of a domain behavior) into their own
subfolder(s) alongside the layer-mirroring ones once more than one such file
accumulates; a single flat guard file does not need its own folder. Only move a file
out of its natural layer folder when doing so would require editing production
code that references its path — leave it flat rather than break that cross-reference.

## Naming Conventions

| Element | Pattern | Example |
|---------|---------|--------|
| Test file | `test_{module}.py` | `test_order_service.py` |
| Test class | `Test{ClassName}` | `TestOrderService` |
| Test method | `test_{method}_{scenario}_{expected}` | `test_process_order_empty_input_raises_error` |
| Fixture | `{noun}_fixture` or `sample_{noun}` | `sample_order` |

## Test Template

```python
"""Tests for {module_name}."""

import pytest
from hypothesis import given, strategies as st


class TestSymbol:
    """Tests for Symbol."""

    def test_method_happy_path(self) -> None:
        """Method returns expected result for valid input."""
        # Arrange
        input_data = ...

        # Act
        result = Symbol().method(input_data)

        # Assert
        assert result == expected

    def test_method_empty_input(self) -> None:
        """Method handles empty input gracefully."""
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
    def test_method_parametrized(self, input_val: int, expected: str) -> None:
        """Method maps input to correct output."""
        assert Symbol().method(input_val) == expected

    @given(st.integers(min_value=0, max_value=100))
    def test_method_property(self, value: int) -> None:
        """Method output is always non-negative."""
        result = Symbol().method(value)
        assert result >= 0
```

## Fixture Patterns

### Factory Fixtures (preferred)

```python
@pytest.fixture
def order_factory():
    """Create test orders with sensible defaults."""

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
- Never use `time.sleep()` in tests — this also covers *indirect* sleeps: a
  `tenacity`-decorated function under test (`@retry(wait=wait_exponential(...))`)
  sleeps for real between attempts unless the test neutralizes it with
  `monkeypatch.setattr("tenacity.nap.time.sleep", lambda _seconds: None)`
- Never use mutable defaults in fixtures
- Never construct an expensive fixture-equivalent (app boot, `TestClient`,
  DB engine) *inside* a `@given(...)`-decorated function body — Hypothesis
  re-invokes the function per generated example (default 100), so the cost is
  paid up to 100x. Build it once outside the loop, then wrap only the
  data-dependent assertions in a small `@given`-decorated inner function called
  once: `with _configured_client() as client: ... ; @given(...) \n def check(...): ... \n check()`

## Diagnosing slow tests

Never guess which tests are slow — measure. `pytest --durations=25` (already
wired into `task test:durations`, see Taskfile) ranks the slowest `call`/`setup`
phases; a fast tier legitimately dominated by *collection* time (imports) rather
than `call` time means the fix is import/fixture hygiene, not deleting tests.
Investigate before assuming test *count* is the problem — a real, evidenced
per-test cost (a genuine sleep, a re-booted app, an unmocked network call)
is usually a handful of tests, not the whole suite.

## Automated speed-hygiene guard

`.agents/skills/testing-conventions/scripts/check_test_hygiene.py` statically
guards two things ruff's `PT` rules do not cover, across every fast-tier module
(`tests/unit`, `tests/property`): a top-level import of a heavy package
(`langchain`, `langsmith`, `matplotlib`, `plotly`, `seaborn` — these load during
*collection*, before deselection even applies) and a real `time.sleep()` call.
Wired into the project's `guard` task and pre-commit; run standalone with
`uv run python .agents/skills/testing-conventions/scripts/check_test_hygiene.py`.

## Anti-Patterns

| Anti-Pattern | Correct Pattern |
|-------------|----------------|
| Testing private methods | Test through public API |
| `time.sleep()` in tests | Use `pytest-timeout` or mocks |
| Real `tenacity` backoff sleep via a retry-decorated function under test | `monkeypatch.setattr("tenacity.nap.time.sleep", lambda _s: None)` |
| App/`TestClient`/DB engine constructed inside a `@given` body | Hoist construction outside the loop; wrap only the draw+assert in an inner `@given` function |
| Shared mutable state | Factory fixtures |
| `assert True` / `assert not False` | Assert specific values |
| Exact float comparison | `pytest.approx()` |
| Ignoring test warnings | Fix root cause |

## Verification

Ruff's `PT` rules police pytest API usage but not file/class naming. Run
`scripts/check_test_naming.py` to check the two naming rules above — every
test file matches `test_*.py`, and every *collected* test class (i.e. not a
private test-double like `_FakeRepo`, which pytest never collects) starts with
`Test`:

```shell
uv run python .agents/skills/testing-conventions/scripts/check_test_naming.py [dir]
```

Defaults to scanning `tests` when no directory is given. Exit code `0` = no
violations.

Run `scripts/check_test_hygiene.py` to enforce fast-tier **speed** hygiene — no
heavy top-level imports (`langsmith`, `langchain`, `matplotlib`, `seaborn`,
`plotly`) and no real `time.sleep()` in `tests/unit`/`tests/property` (both load
or block during the always-run tier):

```shell
uv run python .agents/skills/testing-conventions/scripts/check_test_hygiene.py [dir ...]
```

Both guards run in pre-commit (`test-hygiene-guard`) and `task guard`. Profile
tier cost with `task test:durations` (slowest tests) and `task test:collect-time`
(import/discovery overhead) before deleting tests — collection cost, not count,
is usually the bottleneck. `task test:parallel` (pytest-xdist) is opt-in and
helps only when collection is cheap (repo + venv excluded from antivirus and
OneDrive). A `not slow` test over 8s is flagged by
`tests/conftest.py::pytest_terminal_summary`.
