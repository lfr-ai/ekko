---
description: Specification-Driven Development — scenario authoring rules for Ekko specs
applyTo: "docs/specs/**/*.md"
---

# SDD Instructions

Apply these rules to all files in `docs/specs/`.

## Core Rule

Every spec scenario must have a corresponding passing automated test.
A spec without a passing test is documentation rot.

## Scenario Structure

Use Given-When-Then with **concrete values**:

```markdown
## Scenario: Submit 10-second English audio returns 202 with integer ID

**Given** a 10-second WAV audio file with English speech
**When** the client POSTs the file to `POST /api/v1/transcriptions`
**Then** the response status is `202 Accepted`
**And** the response body contains `{"id": <integer>, "status": "pending"}`
```

## Concrete Values Required

| Avoid | Use instead |
|-------|-------------|
| "some audio" | "a 10-second WAV file" |
| "a valid request" | "a POST to /api/v1/transcriptions with a WAV file" |
| "an error is returned" | "the response status is 422 Unprocessable Entity" |
| "the data is saved" | "a transcription record exists in the database with language = 'en'" |

## No Implementation Details

Specs describe WHAT, not HOW:

```markdown
# Bad — describes implementation
Given the AudioProcessor calls faster-whisper with chunk_size=512

# Good — describes observable behavior
Given a 10-second English WAV audio file
```

## Scenario Naming

Follow: `{Action} {context/input} {expected outcome}`

- `Submit valid English audio returns transcription ID`
- `Submit audio shorter than 500ms is rejected with 422`
- `Delete non-existent transcription returns 404`

## File Organization

One feature file per domain concept. Keep files small (≤ 10 scenarios).
Organize under the correct bounded context directory.

## Spec → Test Link

Every test that implements a scenario must cite the spec in its docstring:

```python
async def test_submit_valid_audio_returns_id(...) -> None:
    """Spec: transcription/transcription-creation.md
    Scenario: Submit valid English audio and receive a transcription ID.
    """
```

## Sync Policy

When behavior changes:

1. Update the spec scenario first.
2. Update the test to match.
3. Update the implementation.
4. All three committed together.
