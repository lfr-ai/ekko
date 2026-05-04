---
description: Specification-Driven Development rules for docs/specs/ scenario files
paths:
  - "docs/specs/**/*.md"
---

# SDD Rules

## Core Rule

Every scenario in `docs/specs/` must have a corresponding passing automated test.
A spec without a test is documentation rot.

## Scenario Format

Given-When-Then with concrete values (real numbers, real HTTP codes, real strings):

```markdown
## Scenario: Submit 10-second English audio returns 202 with integer ID

**Given** a 10-second WAV audio file with English speech
**When** the client POSTs to `POST /api/v1/transcriptions`
**Then** the response status is `202 Accepted`
**And** the body contains `{"id": <integer>, "status": "pending"}`
```

## Prohibited in Specs

- Vague inputs: "some audio", "a valid request"
- Implementation details: "calls faster-whisper with chunk_size=512"
- Vague outcomes: "an error is returned" (use the exact status code)

## Test Link

Every implementing test cites the spec in its docstring:

```python
async def test_submit_valid_audio_returns_id(...) -> None:
    """Spec: transcription/transcription-creation.md
    Scenario: Submit 10-second English audio returns 202 with integer ID.
    """
```

## Sync Policy

When behavior changes: update spec → update test → update implementation.
All three change in the same commit.
