---
description: Repository development conventions for voice-bot
applyTo: "**"
---

# voice-bot — Development Instructions

## Architecture and Boundaries

- Follow Clean Architecture dependency direction: `presentation/infrastructure -> application -> core`.
- `src/voice/core/` must remain framework-independent.
- `src/voice/application/` can import from `core` and configuration, but not concrete adapters.
- `src/voice/infrastructure/` implements protocols declared in `core`.

-## Tooling and Commands

- Use `uv` for dependency and command execution (PDM supported as fallback).
- Preferred project commands are in `Taskfile.yml`.
- Run `task check` (or equivalent lint + tests) before finalizing changes.

## Quality Rules

- Keep changes minimal and scoped.
- Update docs in the same change when behavior or setup changes.
- Use typed Python signatures and avoid `Any` unless truly unavoidable.

## Security Rules

- Never commit secrets.
- Keep `.env.example` updated when new environment variables are introduced.
