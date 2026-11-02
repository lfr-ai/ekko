---
description: Test-Driven Development workflow and test quality rules
applyTo: "tests/**/*.py"
---

# TDD Instructions

Apply these rules to all test code. Cycle mechanics and guardrails live in the
`tdd` skill; markers, factories, and fixture patterns live in
`testing-conventions` — pull up both for deep patterns.

## The Three Laws

1. No production code without a failing test that requires it.
2. No more test code than is sufficient to fail.
3. No more production code than is sufficient to pass.

## Rules

- Red-Green-Refactor: write failing test → minimal implementation → refactor.
  Each cycle takes 1–5 minutes; break into smaller steps if taking longer.
- Test names follow `test_{method}_{scenario}_{expected}`.
- Every test carries a marker: `unit`, `integration`, `asyncio`, `slow`, `property`.
- Use protocol-conforming fakes and factory-boy factories, not `MagicMock`.
- Every bug fix requires a failing regression test first (RED → GREEN → commit
  test and fix together).
- Every protocol in `core/ports/` has a contract test suite wired against all
  concrete implementations.
- Separate Arrange-Act-Assert phases with blank lines; no merged phases.

Coverage policy lives in the repository's coverage configuration and CI
pipeline — do not duplicate numeric thresholds here (they drift).
