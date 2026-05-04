---
name: sdd
description: >
  Specification-Driven Development (Specification by Example) for Ekko. Covers
  Given-When-Then scenario authoring, executable specs, living documentation, and
  the spec-first workflow that bridges product requirements and automated tests.
---

# Skill: Specification-Driven Development (SDD)

SDD for Ekko uses **Specification by Example**: concrete, executable scenarios
written before any implementation. A spec is simultaneously a requirements document,
a test, and living documentation — they are the same artifact.

---

## Core Principle

> "The spec is the test. The test is the spec."

Every significant behavior in Ekko must have a spec scenario that:

1. Describes the behavior in business language (Given-When-Then).
2. Maps directly to a passing automated test.
3. Lives in `docs/specs/` and stays in sync with the code.

---

## Spec Directory Structure

```text
docs/specs/
├── audio-processing/
│   ├── recording-session.md      # AudioSession scenarios
│   └── audio-chunking.md         # Chunk boundary scenarios
├── transcription/
│   ├── transcription-creation.md # Core transcription scenarios
│   ├── language-detection.md     # Language detection edge cases
│   └── pii-anonymization.md      # PII scrubbing scenarios
├── conversation/
│   ├── conversation-turns.md     # Multi-turn dialogue scenarios
│   └── summary-integration.md    # Summary → conversation flow
└── ai-pipeline/
    ├── summarization.md           # Summarization scenarios
    └── embedding-search.md        # RAG/embedding search scenarios
```

---

## Scenario Format (Given-When-Then)

Every scenario follows the Given-When-Then structure.
Use **concrete values** — avoid vague terms like "some audio" or "a valid request".

### Spec File Format

```markdown
# Feature: Transcription Creation

## Background

A running Ekko backend with an empty database.

---

## Scenario: Submit valid English audio and receive a transcription ID

**Given** a 10-second WAV audio file with English speech
**When** the client POSTs the file to `POST /api/v1/transcriptions`
**Then** the response status is `202 Accepted`
**And** the response body contains `{"id": <integer>, "status": "pending"}`
**And** the transcription record exists in the database with `language = "en"`

---

## Scenario: Submit audio shorter than 500ms is rejected

**Given** a 200ms WAV audio file
**When** the client POSTs the file to `POST /api/v1/transcriptions`
**Then** the response status is `422 Unprocessable Entity`
**And** the response body contains `{"detail": "Audio too short: minimum 500ms"}`
```

---

## Spec-First Workflow

### Step 1: Write the Spec

Create or update a file in `docs/specs/{bounded-context}/{feature}.md`.
Use concrete examples. Use domain language (ubiquitous language from DDD skill).

```bash
touch docs/specs/transcription/transcription-creation.md
# Write the scenarios before any code
```

### Step 2: Turn Scenarios into Failing Tests

Map each scenario to a pytest test. Keep the scenario text in the test docstring
so the living documentation link is explicit.

```python
# tests/integration/api/test_transcription_creation.py
import pytest
from httpx import AsyncClient


@pytest.mark.integration
async def test_submit_valid_english_audio_returns_id(
    client: AsyncClient,
    sample_wav_10s: bytes,
) -> None:
    """Spec: transcription/transcription-creation.md
    Scenario: Submit valid English audio and receive a transcription ID.
    """
    # Given a 10-second WAV audio file with English speech
    # When the client POSTs the file to POST /api/v1/transcriptions
    response = await client.post(
        "/api/v1/transcriptions",
        files={"audio": ("sample.wav", sample_wav_10s, "audio/wav")},
    )

    # Then the response status is 202 Accepted
    assert response.status_code == 202
    data = response.json()
    # And the response body contains an integer ID and "pending" status
    assert isinstance(data["id"], int)
    assert data["status"] == "pending"


@pytest.mark.integration
async def test_submit_short_audio_is_rejected(
    client: AsyncClient,
    sample_wav_200ms: bytes,
) -> None:
    """Spec: transcription/transcription-creation.md
    Scenario: Submit audio shorter than 500ms is rejected.
    """
    response = await client.post(
        "/api/v1/transcriptions",
        files={"audio": ("short.wav", sample_wav_200ms, "audio/wav")},
    )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert "Audio too short" in detail
```

### Step 3: Run and Watch Fail (RED)

```bash
uv run pytest tests/integration/api/test_transcription_creation.py -x -v
# Expected: FAILED — route doesn't exist yet
```

### Step 4: Implement Until GREEN

Build each layer from inside out (core → application → presentation).
Use the TDD inner loop for each component.

### Step 5: Confirm Spec Fulfilled

```bash
uv run pytest tests/integration/api/test_transcription_creation.py -v
# Expected: PASSED — all scenarios implemented
```

### Step 6: Keep Spec and Test in Sync

When behavior changes, update **both** the spec file and the test together
in the same commit. A spec without a passing test is a lie.

---

## Scenario Naming Conventions

| Pattern | Good Example |
|---------|-------------|
| Happy path | `Submit valid English audio returns transcription ID` |
| Validation | `Submit audio shorter than 500ms is rejected` |
| Edge case | `Submit audio with no speech returns empty transcript` |
| Error handling | `Submit corrupt WAV file returns 400 with error detail` |
| State transition | `Completed transcription cannot be deleted` |

---

## Spec Quality Rules

1. **Concrete values**: Use real numbers, real strings, real HTTP codes.
2. **One behavior per scenario**: Do not chain unrelated behaviors.
3. **No implementation details**: Specs describe WHAT, not HOW.
4. **Ubiquitous language**: Use domain terms (see DDD skill).
5. **Runnable**: Every scenario maps to an automated test that CI runs.

### Anti-Patterns to Avoid

```markdown
# BAD — vague, no concrete values
Scenario: Submit audio and get a response

# GOOD — concrete, unambiguous
Scenario: Submit 10-second English WAV and receive 202 with integer ID

# BAD — describes implementation
Given the AudioProcessor calls faster-whisper with chunk_size=512

# GOOD — describes behavior
Given a 10-second English WAV audio file
```

---

## Spec Templates

### API Endpoint Spec Template

```markdown
# Feature: {Feature Name}

## Background

{System preconditions — database state, running services, etc.}

---

## Scenario: {Happy path — descriptive name}

**Given** {concrete precondition}
**When** {concrete action with real HTTP method and path}
**Then** {concrete observable outcome with real status code}
**And** {additional assertions}

---

## Scenario: {Validation failure — descriptive name}

**Given** {invalid or edge-case input}
**When** {same action}
**Then** {error response with exact status code and message}
```

### Domain Behavior Spec Template

```markdown
# Feature: {Aggregate/Domain Concept}

---

## Scenario: {Invariant enforcement}

**Given** {aggregate state that violates an invariant}
**When** {mutation attempted}
**Then** {DomainError raised with exact message}

---

## Scenario: {Successful state transition}

**Given** {valid aggregate state}
**When** {valid mutation applied}
**Then** {new aggregate has expected values}
```

---

## Living Documentation

Specs must stay **current and passing**. Stale specs are worse than no specs.

### CI Enforcement

All spec-linked tests run in CI. A broken spec test blocks merge:

```bash
task test:integration   # runs all spec-linked tests
```

### Spec Review on Feature Changes

When modifying existing behavior:

1. Update the spec in `docs/specs/` first.
2. Update the test to match the new scenario.
3. Update the implementation.
4. All three change together in the same PR.

---

## Quick Checklist

- [ ] Spec file exists in `docs/specs/{context}/{feature}.md` before any code
- [ ] Each scenario uses concrete values (no "some", "valid", "a request")
- [ ] Scenario maps 1:1 to a pytest test with a docstring citing the spec
- [ ] Spec uses ubiquitous language (domain terms from the DDD skill)
- [ ] No implementation details in the spec (WHAT not HOW)
- [ ] Tests are passing (spec → test → code → GREEN)
- [ ] Spec and test updated together when behavior changes
- [ ] Spec file committed alongside the implementing code
- [ ] CI runs all spec-linked tests on every PR
