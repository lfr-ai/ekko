# 0001 - Clean Architecture enforcement

Status: Proposed

Date: 2026-04-28

Context
-------

The codebase must follow Clean Architecture: core (business rules) at the
center, application layer for use-cases, and outer adapters for infrastructure
and presentation. This ensures testability and maintainability.

Decision
--------

1. Enforce dependencies direction: presentation/infrastructure -> application -> core.
2. Keep `src/voice/core` framework-independent; only protocols and pure domain code.
3. Application services depend on `core` protocols only; concrete implementations
   live under `infrastructure`.
4. Add automated checks via `scripts/check_architecture_boundaries.py` and run in CI.

Consequences
------------

- Easier testing and reasoning about business logic.
- Clear responsibilities for new contributors.
- CI will prevent accidental boundary violations.
