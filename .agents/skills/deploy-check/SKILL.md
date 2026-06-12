---
name: deploy-check
description: Pre-deployment checklist and build verification. Use before building the PyInstaller EXE or deploying.
disable-model-invocation: true
effort: high
argument-hint: "[target]"
allowed-tools:
  - Bash(task *)
  - Bash(git status *)
  - Bash(git log *)
---

# Deploy Check

Pre-deployment verification for the Ekko desktop application.

## Checklist

Run each step and verify it passes:

1. **All tests pass**: `task test`
2. **No lint errors**: `task lint`
3. **Type check clean**: `task typecheck`
4. **No uncommitted changes**: `git status`
5. **Database migrations up to date**: `task db:migrate`

## Build

Run: `task build:exe`

This produces a standalone PyInstaller EXE.

## Post-Build Verify

- Check the built EXE starts without errors
- Verify audio capture initializes
- Confirm the web UI loads at localhost:8000
