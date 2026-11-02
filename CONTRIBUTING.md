# Contributing

## Quick Reference

1. Fork and create a branch (`feature/...`, `fix/...`, `chore/...`)
2. Install: `task install`
3. Develop following project conventions
4. Validate: `task verify`
5. Commit: `cz commit` (Conventional Commits enforced)
6. Push and open a pull request

## Setup

```bash
task install
cp .env.example .env.local  # Add your API keys
task db:migrate
```

**Prerequisites**: Python 3.14, Node.js 20+, [uv](https://astral.sh/uv), [Bun](https://bun.sh), [Task](https://taskfile.dev)

## Validation

```bash
task verify     # Pre-push: lint + typecheck + tests + xenon + hooks
task ci:local   # Full CI mirror (critical changes only)
```

Pre-commit hooks install automatically via `task install`. They enforce formatting, linting, type checking, security scanning, and architecture boundaries.

## Conventions

### Python

- Python 3.14, full type hints, Google-style docstrings
- `@dataclass(frozen=True, slots=True, kw_only=True)` for value types
- Named constants (no magic numbers/strings)
- Structured logging via `logging.getLogger(__name__)` (never `print()`)
- Exception chaining: `raise X(...) from err`

### Architecture

Clean Architecture — dependencies flow inward: `presentation/infrastructure → application → core`.
See [docs/architecture.md](docs/architecture.md) for the full layer breakdown.

### Testing

- `tests/unit/` (fast, isolated) · `tests/integration/` (DB, API) · `tests/property/` (Hypothesis)
- factory-boy for test data · Coverage target ≥80%

### Frontend

React 19 + TypeScript strict + Tailwind v4 + shadcn/ui · No `any`

## Commits & Branches

Format: `type(scope): subject` — Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `ci`, `build`

Branches: `feature/...`, `fix/...`, `chore/...`, `docs/...`

## Code of Conduct

Participation in this project is governed by [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Security

Secrets are scanned on commit via `detect-secrets`. Update baselines only after confirming false positives:

```bash
cd backend && uv run detect-secrets scan --update ../.secrets.baseline
```

## Pull Requests

1. `task verify` passes
2. Docs updated for API/behavior changes
3. Tests added for new functionality
4. Review requested from maintainers

## License

By contributing, you agree your contributions are licensed under the MIT License.
