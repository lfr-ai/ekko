---
description: Test-Driven Development workflow and test quality rules for Ekko
applyTo: "tests/**/*.py"
---

# TDD Instructions

Apply these rules to all code in `tests/`.

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
def test_transcription_with_no_entries_returns_empty_full_text() -> None: ...
def test_language_with_unsupported_code_raises_validation_error() -> None: ...

# Bad
def test_transcription() -> None: ...
def test_works() -> None: ...
```

## Markers (required on every test)

```python
@pytest.mark.unit         # Fast, no I/O — < 10 ms
@pytest.mark.integration  # DB, API boundary
@pytest.mark.asyncio      # Async test functions
@pytest.mark.slow         # Long-running (> 2s)
```

## Fakes over Mocks

Use protocol-conforming fakes from `tests/mocks/`, not `MagicMock`:

```python
# Good — type-safe, catches interface changes
from tests.mocks.fake_transcription_repo import FakeTranscriptionRepository
repo = FakeTranscriptionRepository()

# Bad — invisible to type checker, doesn't catch protocol changes
repo = MagicMock(spec=TranscriptionRepository)
```

## Bug Fixes

Every bug fix requires a **failing regression test first**:

1. Write test that reproduces the bug (RED).
2. Fix the bug (GREEN).
3. Commit test and fix together.

## Contract Tests

Every protocol in `core/interfaces/` must have a contract test suite in
`tests/unit/core/interfaces/`. Wire it against all concrete implementations.

## Arrange-Act-Assert

Use blank lines to separate the three phases. No merged phases.

```python
def test_example() -> None:
    # Arrange
    repo = FakeTranscriptionRepository()
    transcription = TranscriptionFactory()

    # Act
    await repo.save(transcription=transcription)
    result = await repo.get_by_id(transcription_id=transcription.id)

    # Assert
    assert result == transcription
```

## Coverage

Minimum 70% coverage. Run `task test:coverage` to check.
