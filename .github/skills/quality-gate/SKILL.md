---
name: quality-gate
description: Run full validation suite before finalizing any change. Use after implementing features or fixes.
disable-model-invocation: true
effort: high
argument-hint: "[scope: unit|full|check]"
---

# Quality Gate

Run these validation steps in order. Fix any failures before proceeding.
This project is managed by **uv** and **Task**: every command below must be run
via `task` or `uv run`. Never invoke `pdm`, `poetry`, `pipenv`, `conda`, `pip`,
or bare `python`/`pytest`.

## Quick Validation

For fast feedback during development:

```bash
uv run pytest tests/
uv run ruff check src/ tests/
```

## Full completion gate

Run the project-owned gates instead of reconstructing them manually:

```bash
task test
task check
openspec validate --all
```

## Component-Specific Checks

```bash
uv run pytest -m unit          # Unit tests only (fast)
uv run pytest -m integration   # Integration tests (slower)
uv run pytest -m property      # Property-based tests
```

## On Failure

### Test Failures
- Fix all failing tests before proceeding
- Check test output for specific assertion failures
- Review recent changes that may have broken tests
- Run `uv run pytest -v` for verbose output

### Lint Errors
- Auto-fix most issues: `uv run ruff check --fix src/ tests/`
- Review remaining manual fixes
- Check for import order issues
- Verify no unused imports

### Type Errors
- Fix type annotations
- Add missing type hints
- Resolve `Any` types
- Check protocol implementations

## Pre-Push Checklist

Before pushing to remote:

- [ ] All tests pass: `task test`
- [ ] No lint errors: `uv run ruff check .`
- [ ] Type check clean: `uv run ty check src tests scripts`
- [ ] Pre-commit hooks pass: `uv run pre-commit run --all-files`
- [ ] OpenSpec specs validated: `openspec validate --all`
- [ ] Documentation updated if behavior changed
- [ ] Environment template updated if new env vars added
- [ ] No stray package-manager artifacts (`.pdm-python`, `poetry.lock`)

## Quality Metrics

Target coverage by layer:

| Layer | Minimum Coverage |
|-------|-----------------|
| Core | 90% |
| Application | 80% |
| Infrastructure | 60% |
| Presentation | 70% |

Check coverage: `uv run pytest --cov=src --cov-report=term-missing`
