---
description: Testing standards for Python tests
applyTo: "tests/**/*.py, **/test_*.py, **/conftest.py"
---

# Testing Instructions

Full test templates, fixture patterns, and anti-patterns live in the
`testing-conventions` skill (`.agents/skills/testing-conventions/SKILL.md`).

- Write focused tests with clear Arrange/Act/Assert structure.
- Prefer behavior-oriented assertions over implementation details; assert
  specific values, never vague truthiness.
- Add a regression test for every bug fix.
- Avoid flaky time/network dependencies unless explicitly integration-scoped.
- For HTTP status assertions, use constants from `fastapi.status` instead of
  numeric literals.
- Use `pytest.raises(ExcType, match="...")` — never a bare `pytest.raises(ExcType)`.
- Add a docstring when the behavior under test is not clear from the test name
  and assertions.
- Do not use real `time.sleep()` in unit or property tests; control time or
  patch the delay instead.

## Test markers and tasks

Both pytest configurations register `unit`, `integration`, `property`,
`performance`, and `slow` markers. Mark tests according to their dependencies
and runtime.

```bash
task test             # backend + repository + frontend unit tests
task test:all         # full backend and repository Python suites + frontend unit tests
task test:integration # backend integration tests
task test:e2e         # browser end-to-end tests
```

The root and backend test suites have separate pytest configurations. Keep them
separate when invoking pytest directly.

## Coverage

Treat the repository's coverage configuration and CI pipeline as the only
coverage-policy source — do not duplicate numeric thresholds here (they drift).
