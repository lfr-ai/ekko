---
name: quality-gate
description: Run full validation suite before finalizing any change. Use after implementing features or fixes.
disable-model-invocation: true
effort: high
argument-hint: "[scope: unit|full|check]"
allowed-tools:
  - Bash(task *)
  - Bash(uv run *)
  - Bash(python -m pytest *)
  - Bash(python -m ruff *)
---

# Quality Gate

Run these validation steps in order. Fix any failures before proceeding.

## Steps

1. **Unit tests**: `task test:unit`
2. **Lint**: `task lint`
3. **Type check**: `task typecheck`

## Full CI-equivalent

For comprehensive validation run: `task check`

This runs: lint + test:unit + typecheck + xenon (cyclomatic complexity).

## On Failure

- Fix all test failures before proceeding
- Fix all lint errors (`uv run ruff check --fix .` auto-fixes most)
- Fix all type errors
- If xenon fails, reduce cyclomatic complexity of the flagged functions
