---
name: tdd
description: >
  Test-Driven Development workflow for Ekko. Covers the Red-Green-Refactor cycle,
  acceptance TDD outer loop, unit TDD inner loop, contract testing for ports,
  and the test pyramid.
paths:
  - "tests/**/*.py"
---

# Skill: Test-Driven Development (TDD)

## The Three Laws of TDD

1. **No production code** without a failing test that requires it.
2. **No more test** than is sufficient to fail (compilation failure counts).
3. **No more production code** than is sufficient to pass the failing test.

---

## The Red-Green-Refactor Cycle

```text
  ┌─────────────────────────────────────────────────────┐
  │                                                     │
  │   RED ──────────────► GREEN ──────────────► REFACTOR│
  │    │                   │                       │    │
  │  Write a             Make it               Clean up │
  │  failing test        pass with           without    │
  │  that describes      minimal code        breaking   │
  │  the behavior        change              the tests  │
  │                                               │     │
  │   ◄──────────────────────────────────────────┘     │
  │                 Repeat                              │
  └─────────────────────────────────────────────────────┘
```

Each cycle should take **1–5 minutes**. If a cycle takes longer, the step is too large.
Break it into smaller increments.

---

## Two TDD Loops

### Outer Loop: Acceptance TDD

Drives a complete feature from the outside in.
Write an integration or acceptance test **before any production code exists**.

```python
# tests/integration/api/test_transcription_api.py
import pytest
from httpx import AsyncClient

@pytest.mark.integration
async def test_submit_audio_returns_transcription_id(client: AsyncClient) -> None:
    # Given a valid audio file
    audio_bytes = load_fixture("sample.wav")

    # When the audio is submitted to the API
    response = await client.post(
        "/api/v1/transcriptions",
        files={"audio": ("sample.wav", audio_bytes, "audio/wav")},
    )

    # Then a transcription job is created and an ID is returned
    assert response.status_code == 202
    data = response.json()
    assert "id" in data
    assert isinstance(data["id"], int)
```

This test will be **RED** immediately. It drives the full stack:
route → service → repository → database.

### Inner Loop: Unit TDD

Drives each small piece of implementation inside the outer loop.
One failing unit test → minimum code → refactor. Repeat.

```python
# tests/unit/core/entities/test_transcription.py
import pytest
from ekko.core.entities.transcription import Transcription
from ekko.core.value_objects.language import Language
from ekko.core.exceptions import TranscriptionError
from tests.factories import TranscriptionEntryFactory

@pytest.mark.unit
def test_transcription_full_text_joins_entries() -> None:
    # Arrange
    lang = Language(code="en")
    entries = (
        TranscriptionEntryFactory(text="Hello"),
        TranscriptionEntryFactory(text="world"),
    )
    transcription = Transcription(id=1, language=lang, entries=entries)

    # Act
    result = transcription.full_text

    # Assert
    assert result == "Hello world"


@pytest.mark.unit
def test_transcription_rejects_unsorted_entries() -> None:
    lang = Language(code="en")
    entries = (
        TranscriptionEntryFactory(text="second", offset=2.0),
        TranscriptionEntryFactory(text="first", offset=0.5),
    )

    with pytest.raises(TranscriptionError, match="ordered by offset"):
        Transcription(id=1, language=lang, entries=entries)
```

---

## Contract Testing for Ports

Every protocol in `core/ports/` must have a **contract test suite** in
`tests/unit/core/ports/`. Any adapter that implements the protocol must
pass the contract tests.

```python
# tests/unit/core/ports/test_transcription_repository_contract.py
"""Contract tests for the TranscriptionRepository port.

Run these against every concrete implementation by parametrizing the fixture.
"""
import pytest
from ekko.core.ports import TranscriptionRepository
from tests.factories import TranscriptionFactory


@pytest.mark.unit
async def test_repository_saves_and_retrieves(
    repo: TranscriptionRepository,
) -> None:
    # Arrange
    transcription = TranscriptionFactory()

    # Act
    await repo.save(transcription=transcription)
    result = await repo.get_by_id(transcription_id=transcription.id)

    # Assert
    assert result is not None
    assert result.id == transcription.id
    assert result.language == transcription.language


@pytest.mark.unit
async def test_repository_returns_none_for_missing_id(
    repo: TranscriptionRepository,
) -> None:
    result = await repo.get_by_id(transcription_id=99999)
    assert result is None
```

Wire the contract against both real and fake implementations:

```python
# tests/conftest.py
import pytest
from tests.mocks.fake_transcription_repo import FakeTranscriptionRepository

@pytest.fixture(params=["fake"])
def repo(request):
    if request.param == "fake":
        return FakeTranscriptionRepository()
    # Add SQLAlchemy implementation in integration tests
```

---

## Test Pyramid

```text
          /\
         /  \  E2E tests (few, slow, catch full-stack regressions)
        /────\
       /      \  Integration tests (medium — DB, API boundary)
      /────────\
     /          \  Unit tests (many, fast, isolated — the foundation)
    /────────────\
```

| Level | Count | Speed | Scope |
|-------|-------|-------|-------|
| Unit | Many | < 10 ms each | Single function/class, no I/O |
| Integration | Medium | < 2 s each | DB + API boundary |
| E2E | Few | > 5 s each | Full stack, real browser or client |

**Golden ratio**: aim for ~70% unit, ~20% integration, ~10% e2e.

---

## TDD Workflow for a New Feature

Follow this sequence for every new feature or bug fix:

### 1. Write the Acceptance Test (Outer RED)

```bash
# Example: adding a DELETE /transcriptions/{id} endpoint
# Write tests/integration/api/test_delete_transcription.py first
```

### 2. Run and Watch It Fail

```bash
uv run pytest tests/integration/api/test_delete_transcription.py -x -v
# Expected: FAILED (404 or AttributeError — route doesn't exist yet)
```

### 3. Drive the Domain with Unit Tests (Inner RED → GREEN → REFACTOR)

For each layer from inside out (core → application → presentation):

```bash
# Write unit test → run → RED
uv run pytest tests/unit/core/... -x -v

# Write minimum implementation → run → GREEN
uv run pytest tests/unit/core/... -x -v

# Refactor → confirm still GREEN
uv run pytest tests/unit/core/... -x -v
```

### 4. Watch the Acceptance Test Go GREEN

```bash
uv run pytest tests/integration/api/test_delete_transcription.py -x -v
# Expected: PASSED
```

### 5. Run the Full Suite

```bash
task test   # All tests must still pass
```

---

## Fake Objects vs Mocks

Prefer **protocol-conforming fakes** over `unittest.mock.MagicMock`.
Fakes are readable, type-safe, and catch interface changes at import time.

```python
# tests/mocks/fake_transcription_repo.py
from ekko.core.entities.transcription import Transcription
from ekko.core.ports import TranscriptionRepository


class FakeTranscriptionRepository:
    """In-memory implementation of TranscriptionRepository for unit tests."""

    def __init__(self) -> None:
        self._store: dict[int, Transcription] = {}

    async def save(self, *, transcription: Transcription) -> None:
        self._store[transcription.id] = transcription

    async def get_by_id(self, *, transcription_id: int) -> Transcription | None:
        return self._store.get(transcription_id)

    async def list_recent(self, *, limit: int) -> list[Transcription]:
        items = sorted(self._store.values(), key=lambda t: t.id, reverse=True)
        return items[:limit]

    async def delete(self, *, transcription_id: int) -> None:
        self._store.pop(transcription_id, None)
```

---

## TDD for Bug Fixes

Every bug fix **must** begin with a failing regression test:

```python
# 1. Write a test that reproduces the bug
@pytest.mark.unit
def test_transcription_duration_is_zero_with_no_entries() -> None:
    """Regression: duration_ms was raising ZeroDivisionError with empty entries."""
    transcription = Transcription(id=1, language=Language(code="en"), entries=())
    assert transcription.duration_ms == 0.0

# 2. Run → RED (reproduces the bug)
# 3. Fix the bug
# 4. Run → GREEN
# 5. Commit both test and fix together
```

---

## TDD Quick Reference

```bash
# Run a single test in watch-mode style
uv run pytest tests/unit/core/entities/test_transcription.py -x -v

# Run with output on failure
uv run pytest tests/ -x -v --tb=short

# Run only fast unit tests during inner loop
uv run pytest tests/unit/ -x -v -q

# Full validation before committing
task test && task lint && task typecheck
```

---

## Quick Checklist

- [ ] A failing test exists before any production code is written
- [ ] Each test describes a single behavior (one assertion per test is ideal)
- [ ] Test names follow `test_{method}_{scenario}_{expected}`
- [ ] Unit tests have zero I/O and run in < 10 ms
- [ ] Ports have contract test suites in `tests/unit/core/ports/`
- [ ] Every bug fix starts with a failing regression test
- [ ] Fakes in `tests/mocks/` implement protocols (no `MagicMock` on core ports)
- [ ] The full test suite is green before every commit
- [ ] No `skip` markers without a GitHub issue reference
- [ ] Coverage stays above 70% (`task test:coverage`)
