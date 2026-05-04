# Contributing

Thank you for contributing! Please read `README.md` and follow the coding conventions in `.github/copilot-instructions.md`.

## Quick Reference

1. Fork the repository
2. Create a feature branch (`feature/your-feature`, `fix/your-fix`, `chore/your-chore`)
3. Install dependencies: `task install`
4. Make your changes following project conventions
5. Run pre-push validation: `task verify`
6. Commit using Conventional Commits: `cz commit`
7. Push and submit a pull request

## Development Setup

### Prerequisites

- Python 3.12+
- Node.js 20+
- [uv](https://astral.sh/uv) (Python package manager)
- [Bun](https://bun.sh) (Frontend package manager)
- [Task](https://taskfile.dev) (Task runner)

### Installation

```bash
# Install all dependencies
task install

# Setup environment
cp .env.example .env.local
# Edit .env.local with your API keys

# Initialize database
task db:migrate
```

> **Note**: This repository is standardized on `uv` for Python dependency management. PDM is not part of the supported contributor workflow.

## Pre-Commit Hooks

Pre-commit hooks provide fast local feedback before you commit changes. They are automatically installed when you run `task install`.

### Manual Installation

If hooks are not yet installed:

```bash
pre-commit install
```

### What Gets Checked

The project enforces several quality gates at commit time:

**Pre-Commit Stage** (runs on `git commit`):

- Code formatting (ruff, biome)
- Linting (ruff, yamllint, markdownlint)
- Type checking (ty)
- Security scanning (detect-secrets, bandit)
- **Architecture boundary validation** - Ensures Clean Architecture dependencies flow inward
- Conventional commit message format

**Pre-Push Stage** (runs on `git push`):

- **Magic string detection** - Flags hardcoded strings that should be constants
- Unit test suite
- Integration checks

### Running Hooks Manually

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run check-architecture-boundaries --all-files
pre-commit run check-magic-strings --all-files --hook-stage pre-push

# Run hooks on staged files only
pre-commit run
```

### Hook Descriptions

- **check-architecture-boundaries**: Validates Clean Architecture import boundaries. Blocks commits with violations
  like `core/` importing from `presentation/` or `application/` importing from `infrastructure/`. Fast (< 3 seconds).

- **check-magic-strings**: Detects hardcoded strings that should be extracted to constants or registry.
  Runs at pre-push stage to allow work-in-progress commits. Provides verbose output with suggested fixes.

### Handling Violations

When a hook fails:

1. Read the error message - it shows the file, line, and reason
2. Fix the violation before committing
3. Run the hook again to verify the fix
4. Commit your changes

If you need to temporarily skip hooks (emergencies only):

```bash
git commit --no-verify
```

**Warning**: Skipping hooks may cause CI failures. Use only when you understand the risk.

## Pre-Push Validation

**Always run `task verify` before pushing** to catch CI failures early.

### Quick Check (< 5 min)

```bash
task verify
```

Runs essential checks:

- Linting (ruff, biome, yaml)
- Type checking (ty, tsc)
- Unit tests
- Cyclomatic complexity (xenon)
- Pre-commit hooks

### Full CI Mirror (< 15 min)

For critical changes (architecture, security, infrastructure), run the full pipeline locally:

```bash
task ci:local
```

Mirrors the complete GitHub Actions pipeline including:

- All linting and formatting checks
- Security scans (bandit, pip-audit, detect-secrets)
- Unit + integration tests
- Architecture boundary validation
- Pre-commit hooks

### Individual Checks

```bash
# Linting
task lint              # All linters
task lint:python       # Python (ruff)
task lint:frontend     # Frontend (biome)

# Type checking
task typecheck         # Python + Frontend

# Testing
task test              # Default tests
task test:unit         # Unit tests only
task test:integration  # Integration tests

# Security
task security:audit    # Dependency audit
task security:scan     # All security scans (bandit + audit + secrets)
task lint:secrets      # Secret scanning

# Code quality
task xenon             # Complexity check
```

### Windows Compatibility

The project uses the `uv run python -m <tool>` pattern for cross-platform CLI invocation, avoiding Windows path resolution issues with script entry points.

## Coding Conventions

### Python

- Python 3.12+ features
- Full type hints on all functions/methods
- Google-style docstrings
- Keyword-only args with `*` separator for 3+ params
- `frozen=True, slots=True` on all dataclasses
- No magic numbers; use named constants
- Structured logging with structlog (never `print()`)
- Exception chaining: `raise NewError(...) from original_error`

See `.github/skills/python-conventions/SKILL.md` for complete guidelines.

### Architecture

Clean Architecture with strict dependency rules:

- `core/` - Pure domain logic (no framework dependencies)
- `application/` - Use case orchestration
- `infrastructure/` - External integrations (DB, APIs)
- `presentation/` - API routes, GraphQL, middleware

**Dependency Rule**: Dependencies always point inward:
`presentation/infrastructure → application → core`

See `.github/skills/clean-architecture/SKILL.md` for boundaries.

### Testing

- Unit tests: `tests/unit/` (fast, isolated, no I/O)
- Integration tests: `tests/integration/` (DB, API, external services)
- Property tests: `tests/property/` (Hypothesis)
- E2E tests: `tests/e2e/` (Playwright)
- Use factory-boy for test data generation
- Coverage target: ≥80% on core + application layers

See `.github/skills/testing-conventions/SKILL.md` for patterns.

### Frontend

- React 19 with TypeScript
- Functional components only
- Tailwind CSS v4
- shadcn/ui for UI components
- Strict TypeScript (no `any`)

## Commit Messages

This repository enforces Conventional Commits. Use Commitizen for validated commit messages:

```bash
# Create a commit using Commitizen
cz commit
# or quick alias
cz c
```

Format: `type(scope): subject`

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`, `build`

**Examples**:

```text
feat(chat): add voice streaming support
fix(db): correct migration rollback logic
docs(readme): update pre-push workflow
test(unit): add property tests for PII anonymizer
```

The repository includes a `.cz.toml` configuration and a pre-commit `commit-msg` hook for validation.

## Branch Naming

- `feature/...` - New features
- `fix/...` - Bug fixes
- `chore/...` - Maintenance, refactoring, tooling
- `docs/...` - Documentation updates

## Security

### Secret Scanning

Secrets are automatically scanned on commit. If you need to add a false positive:

```bash
cd backend && uv run detect-secrets scan --update ../.secrets.baseline
```

Review `.secrets.baseline` before committing to ensure no real secrets were added.

### Security Baselines

- **detect-secrets**: `.secrets.baseline`
- **bandit**: `backend/bandit.toml`

Update baselines only after confirming false positives.

## Pull Request Process

1. Ensure `task verify` passes locally
2. Update documentation if you changed APIs or added features
3. Add tests for new functionality (target ≥80% coverage)
4. Follow the pull request template
5. Request review from maintainers
6. Address review feedback
7. Squash commits before merge (if requested)

## Code Review

All submissions require code review. Reviews check:

- Adherence to Clean Architecture boundaries
- Code quality and conventions
- Test coverage
- Documentation completeness
- Security implications

## Getting Help

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **Email**: <lfr@tik-ai.dk>

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
