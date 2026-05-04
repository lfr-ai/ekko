---
name: testing-conventions
description: Test quality and structure conventions.
---

# Skill: Testing Conventions

## Technology Stack

| Aspect | Tool |
|--------|------|
| Test framework | pytest |
| Async | pytest-asyncio (`asyncio_mode = "auto"`) |
| Factories | factory-boy |
| Property testing | Hypothesis |
| Benchmarks | pytest-benchmark |
| Coverage | pytest-cov (minimum 70%) |
| Time freezing | freezegun |
| HTTP mocking | respx (for httpx) |
| Frontend unit | Vitest + React Testing Library + fast-check |
| Frontend E2E | Playwright |

## Non-Goals

- Do NOT use `unittest.TestCase` — use plain pytest functions
- Do NOT use `mock.patch` on implementation details — mock at boundaries
- Do NOT write tests without markers
- Do NOT leave flaky tests unaddressed
- Do NOT use Jest (Vitest is the frontend test runner)

---

## Test Structure

```text
tests/
├── unit/                # Fast, isolated, no I/O, no network
├── integration/         # Database, API boundary, external services
├── property/            # Hypothesis property-based tests
├── performance/         # pytest-benchmark timing assertions
├── e2e/                 # End-to-end (full stack)
├── database/            # Migration and ORM model tests
├── factories/           # factory-boy factories (shared test data)
├── fixtures/            # Shared fixture data (JSON, audio samples)
├── mocks/               # Reusable mock objects and fakes
└── utils/               # Assertion helpers and test utilities
```

---

## Markers

Every test function must have at least one marker:

```python
import pytest

@pytest.mark.unit
def test_parse_audio_format_returns_wav() -> None:
    ...

@pytest.mark.integration
async def test_repository_persists_transcription() -> None:
    ...

@pytest.mark.asyncio
async def test_async_pipeline_completes() -> None:
    ...

@pytest.mark.slow
def test_full_transcription_pipeline() -> None:
    ...
```

| Marker | Meaning | I/O Allowed |
|--------|---------|-------------|
| `@pytest.mark.unit` | Fast, isolated | No |
| `@pytest.mark.integration` | Boundary tests | Yes (DB, API) |
| `@pytest.mark.asyncio` | Async test function | Depends on other markers |
| `@pytest.mark.slow` | Long-running (> 2s) | Yes |

---

## Test Naming

Follow the pattern `test_{method}_{scenario}_{expected}`:

```python
# Good — descriptive, follows pattern
def test_parse_format_with_valid_wav_returns_audio_format() -> None: ...
def test_parse_format_with_unknown_extension_raises_value_error() -> None: ...
def test_anonymizer_with_email_replaces_with_placeholder() -> None: ...

# Bad — vague, no scenario
def test_parse() -> None: ...
def test_it_works() -> None: ...
```

---

## Arrange-Act-Assert

Structure every test with the AAA pattern. Use blank lines to separate
the three phases:

```python
@pytest.mark.unit
def test_transcription_entry_stores_text_and_offset() -> None:
    # Arrange
    text = "Hello world"
    offset = 1.5

    # Act
    entry = TranscriptionEntry(text=text, offset=offset)

    # Assert
    assert entry.text == text
    assert entry.offset == offset
```

---

## Factories (factory-boy)

All test data creation goes through factories in `tests/factories/`.
Never construct domain objects with raw constructors in tests.

```python
# tests/factories/transcription_factory.py
import factory
from ekko.core.entities.transcription import Transcription

class TranscriptionFactory(factory.Factory):
    class Meta:
        model = Transcription

    id = factory.Sequence(lambda n: n)
    text = factory.Faker("sentence")
    language = "en"
    duration_ms = factory.LazyFunction(lambda: 5000)
```

Usage in tests:

```python
from tests.factories.transcription_factory import TranscriptionFactory

@pytest.mark.unit
def test_transcription_has_default_language() -> None:
    transcription = TranscriptionFactory()
    assert transcription.language == "en"

# Override specific fields
@pytest.mark.unit
def test_transcription_with_custom_language() -> None:
    transcription = TranscriptionFactory(language="da")
    assert transcription.language == "da"
```

---

## Property Testing (Hypothesis)

Property-based tests live in `tests/property/`. Use Hypothesis to test
invariants rather than specific examples:

```python
import pytest
from hypothesis import given, strategies as st
from ekko.core.enums.base import ParseableEnum

class SampleEnum(ParseableEnum):
    A = "a"
    B = "b"

@pytest.mark.unit
@given(value=st.sampled_from(["a", "b", "A", "B", " a ", " B "]))
def test_parseable_enum_roundtrips(value: str) -> None:
    """Parsing any valid value (case-insensitive) produces a valid member."""
    result = SampleEnum.from_str(value)
    assert isinstance(result, SampleEnum)
```

---

## Reusable Mocks

Place reusable mocks and fakes in `tests/mocks/`. Prefer protocol-conforming
fakes over `unittest.mock.MagicMock`:

```python
# tests/mocks/fake_stt_service.py
from ekko.core.interfaces import STTService

class FakeSTTService(STTService):
    """In-memory STT service for testing."""

    def __init__(self, *, result: str = "test transcription") -> None:
        self._result = result

    async def transcribe(self, audio: bytes) -> str:
        return self._result
```

---

## Shared Fixtures

Common fixtures go in `conftest.py` at the appropriate level. Shared
test data (JSON files, audio samples) lives in `tests/fixtures/`:

```python
# tests/conftest.py
import pytest
from tests.mocks.fake_stt_service import FakeSTTService

@pytest.fixture
def fake_stt() -> FakeSTTService:
    return FakeSTTService()

@pytest.fixture
def sample_audio(tmp_path: Path) -> Path:
    audio_file = tmp_path / "sample.wav"
    audio_file.write_bytes(b"RIFF" + b"\x00" * 100)
    return audio_file
```

---

## Async Tests

Use `pytest-asyncio` with `asyncio_mode = "auto"` (configured in
`pyproject.toml`). Async test functions are detected automatically:

```python
@pytest.mark.integration
async def test_repository_saves_and_retrieves() -> None:
    repo = InMemoryTranscriptionRepository()
    entry = TranscriptionFactory()

    await repo.save(entry)
    result = await repo.get_by_id(entry.id)

    assert result == entry
```

---

## Time-Dependent Tests

Use `freezegun` to freeze time in tests that depend on timestamps:

```python
from freezegun import freeze_time

@pytest.mark.unit
@freeze_time("2025-01-15 10:30:00")
def test_created_at_uses_current_time() -> None:
    entry = create_log_entry(message="test")
    assert entry.created_at.isoformat() == "2025-01-15T10:30:00"
```

---

## HTTP Mocking

Use `respx` to mock `httpx` calls in integration tests:

```python
import httpx
import respx

@pytest.mark.integration
@respx.mock
async def test_openai_client_handles_rate_limit() -> None:
    respx.post("https://api.openai.com/v1/chat/completions").mock(
        return_value=httpx.Response(429, json={"error": "rate_limited"})
    )

    with pytest.raises(RateLimitError):
        await client.complete(prompt="test")
```

---

## Benchmarks

Use `pytest-benchmark` in `tests/performance/` for timing assertions:

```python
@pytest.mark.performance
def test_pii_scrub_performance(benchmark) -> None:
    text = "John Doe's email is john@example.com" * 100
    result = benchmark(anonymizer.scrub, text)
    assert "[EMAIL]" in result
```

---

## Coverage

Minimum **70%** code coverage target. Run with:

```bash
task test:coverage    # Generates coverage report
```

Coverage configuration is in `pyproject.toml` under `[tool.coverage]`.

---

## Running Tests

```bash
task test                # Default: backend unit + frontend unit
task test:unit           # Backend unit tests only
task test:integration    # Integration tests only
task test:property       # Hypothesis property-based tests
task test:performance    # Benchmark tests
task test:e2e            # End-to-end tests
task test:frontend       # Frontend unit tests (Vitest)
task test:coverage       # Tests with coverage report
```

---

## Quick Checklist

- [ ] Every test has at least one marker (`@pytest.mark.unit`, etc.)
- [ ] Test names follow `test_{method}_{scenario}_{expected}`
- [ ] Tests use Arrange-Act-Assert structure
- [ ] Test data created via factory-boy factories
- [ ] No raw constructors in test files (use factories)
- [ ] Mocks are protocol-conforming fakes, not `MagicMock`
- [ ] Async tests use `pytest-asyncio` (no manual event loop)
- [ ] Time-dependent tests use `freezegun`
- [ ] HTTP calls mocked with `respx`
- [ ] No I/O in unit tests
- [ ] Coverage meets 70% minimum
