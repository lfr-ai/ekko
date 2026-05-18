# Ekko

AI-powered voice assistant platform with CrewAI agents, GraphQL, and PII anonymization.
Distributed as a standalone Windows EXE.

## 🚀 Quick Links

- **[Complete Setup Guide](docs/TOOLS_SETUP_GUIDE.md)** - Full development environment setup
- **[Claude + GitHub Copilot](docs/CLAUDE_COPILOT_GUIDE.md)** - Use Claude AI for development
- **[Agent Customization](.github/agents/README.md)** - Custom AI development agents
- **[Contributing](CONTRIBUTING.md)** - Contribution guidelines
- **[Security Policy](SECURITY.md)** - Security and vulnerability reporting

## ✨ Features

- 🎤 **Real-time Voice Streaming** - Low-latency audio capture and processing
- 🤖 **AI-Powered Conversations** - LLM integration with CrewAI multi-agent system
- 🔒 **PII Anonymization** - Regex-based sensitive data scrubbing
- 📊 **GraphQL + REST** - Flexible API layer with subscriptions
- 🧪 **Comprehensive Testing** - Unit, integration, property-based, and E2E tests
- 🛠️ **Modern Tooling** - AI code review, OpenAPI docs, Warp workflows

## 🚦 Quickstart

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

### Development

```bash
# Start backend + frontend
task dev

# Or individually:
task dev:backend   # Backend only (port 8000)
task dev:frontend  # Frontend only (port 5173)
```

### Prompt Versioning

Ekko now includes a built-in prompt registry with immutable prompt snapshots.

- Prompt sources are provisioned into version files under `backend/src/ekko/ai/prompts/versions/`.
- When `EKKO_PROMPT_AUTO_PROVISION=true`, changing a source prompt creates a new version on next use.
- Use `EKKO_PROMPT_VERSION` to pin the app to a specific prompt version (e.g. `v2`).

```bash
# Provision/update prompt versions from current prompt sources
task prompts:provision

# List available prompt versions
task prompts:list
```

### Quality Checks

```bash
# Run all quality checks
task check

# Individual checks:
task lint          # Linting (ruff, biome)
task typecheck     # Type checking (mypy, tsc)
task test          # Run tests
task format        # Format code
```

### Pre-Push Validation

Verify that your changes will pass CI before pushing. Use these workflows to catch issues early:

#### Quick Check (< 5 min)

```bash
task verify
```

Runs essential checks that catch 95% of CI failures:

- Linting (ruff, biome, yaml)
- Type checking (ty, tsc)
- Unit tests
- Cyclomatic complexity (xenon)
- Pre-commit hooks

**Windows Note**: Uses `uv run python -m <tool>` pattern for cross-platform compatibility.

#### Full CI Mirror (< 15 min)

```bash
task ci:local
```

Mirrors the complete GitHub Actions pipeline:

1. **Lint & Format** - Fast fail on code quality issues
2. **Security Scans** - bandit, pip-audit, detect-secrets (parallel)
3. **Tests** - Unit tests → Integration tests (sequential)
4. **Architecture** - Clean Architecture boundary validation
5. **Build** - Verify compilation and packaging

#### Security Scanning

```bash
# Run all security checks (bandit + pip-audit + secrets)
task security:scan

# Or run individually:
task security:audit    # Dependency audit only (pip-audit)
task lint:secrets      # detect-secrets baseline scan
cd backend && uv run python -m bandit -c bandit.toml -r src/ekko   # Python security
cd backend && uv run pip-audit                                      # Dependency audit
```

**Baselines**:

- Secret scanning: `.secrets.baseline`
- Bandit security: `backend/bandit.toml`

**Update baselines** after reviewing and confirming false positives:

```bash
cd backend && uv run detect-secrets scan --update ../.secrets.baseline
```

#### CI Pipeline Structure

The GitHub Actions pipeline runs in stages for optimal speed:

```text
┌─────────────────────────────────────────────────────┐
│  Stage 1: Lint & Type Check (fast fail)            │  → 3-5 min
│  - ruff lint + format                               │
│  - ty type check                                    │
│  - pytest unit tests                                │
├─────────────────────────────────────────────────────┤
│  Stage 2: Security (parallel)                       │  → 3-5 min
│  - bandit (Python security)                         │
│  - pip-audit (dependency CVEs)                      │
│  - detect-secrets (credential leaks)                │
├─────────────────────────────────────────────────────┤
│  Stage 3: Integration Tests (after Stage 1)        │  → 5-10 min
│  - Database integration                             │
│  - API integration                                  │
│  - External service mocks                           │
├─────────────────────────────────────────────────────┤
│  Stage 4: Architecture & Validation                 │  → 2-5 min
│  - Clean Architecture boundaries                    │
│  - Link checking (lychee)                           │
│  - ShellCheck                                       │
│  - actionlint (workflow validation)                 │
└─────────────────────────────────────────────────────┘
```

**Total CI time**: ~15-25 minutes
**Local quick check**: ~5 minutes (task verify)
**Local full mirror**: ~15 minutes (task ci:local)

### Build

```bash
# Build standalone Windows EXE
task build:exe

# Build frontend only
task frontend:build
```

## 🏗️ Architecture

Clean Architecture with strict dependency direction:
`presentation/infrastructure → application → core`

```text
┌─────────────────────────────────────────────────────┐
│  Presentation (API routes, GraphQL, middleware)     │  ← FastAPI, Strawberry
├─────────────────────────────────────────────────────┤
│  Application (use case orchestration, services)     │  ← Business logic
├─────────────────────────────────────────────────────┤
│  Core (entities, value objects, domain rules)       │  ← Pure domain
├─────────────────────────────────────────────────────┤
│  Infrastructure (DB, external clients, adapters)     │  ← SQLAlchemy, OpenAI
├─────────────────────────────────────────────────────┤
│  AI (CrewAI agents, PII, chains, embeddings)       │  ← AI pipeline
└─────────────────────────────────────────────────────┘
```

### Tech Stack

**Backend**:

- FastAPI, Uvicorn
- Strawberry GraphQL
- SQLAlchemy, Alembic, SQLite
- CrewAI, LangChain, OpenAI
- Pydantic v2, structlog

**Frontend**:

- React 19, TypeScript
- Vite 6 + SWC
- Tailwind CSS v4
- shadcn/ui (Radix)
- Zustand, TanStack Query
- Storybook

**Testing**:

- pytest, Hypothesis
- Vitest, React Testing Library, fast-check
- Playwright (E2E)
- factory-boy

**Quality**:

- ruff (Python linting/formatting)
- mypy (type checking)
- Biome (frontend linting/formatting)
- pre-commit hooks

**AI Development Tools**:

- GitHub Copilot with Claude 3.5 Sonnet
- CodeRabbit (AI code review)
- Custom VS Code agents
- Warp terminal workflows

## 📚 Documentation

### Core Documentation

- [Complete Setup Guide](docs/TOOLS_SETUP_GUIDE.md) - Full environment setup
- [Architecture Overview](docs/ARCHITECTURE.md) - System design
- [Contributing Guide](CONTRIBUTING.md) - How to contribute
- [Security Policy](SECURITY.md) - Security guidelines

### AI Development

- [Claude + GitHub Copilot Guide](docs/CLAUDE_COPILOT_GUIDE.md) - Use Claude for coding
- [Agent Customization](.github/agents/README.md) - Custom AI agents
- [Agent Instructions](.github/copilot-instructions.md) - Project-specific AI guidance

### Development Guides

- [Clean Architecture](.github/skills/clean-architecture/SKILL.md) - Layer boundaries
- [Python Conventions](.github/skills/python-conventions/SKILL.md) - Code standards
- [Frontend Stack](.github/skills/frontend-react-stack/SKILL.md) - React patterns
- [Testing Conventions](.github/skills/testing-conventions/SKILL.md) - Test strategy
- [Naming Registry](.github/skills/naming-registry/SKILL.md) - Constant management

## 🛠️ Tools

### CodeRabbit (AI Code Review)

Automated AI-powered code reviews on pull requests.

```bash
# Validate configuration
task tools:coderabbit:validate
```

Configuration: `.coderabbit.yaml`

### OpenAPI Documentation

Generate OpenAPI specs and interactive documentation.

```bash
# Generate docs
task tools:openapi:generate

# View in browser
task tools:openapi:view
```

Output: `docs/api/`

### Warp Terminal

Modern terminal with AI features and workflows.

```bash
# Install project workflows
task tools:warp:install
```

Configuration: `.warp/`

### GitNexus

Advanced Git workflow automation.

```bash
# Validate configuration
task tools:gitnexus:validate
```

Configuration: `.gitnexus/config.json`

### Check All Tools

```bash
# Check status of all tools
task tools:status
```

## 🧪 Testing

```bash
# Run all tests
task test

# Specific test types
task test:unit          # Unit tests
task test:integration   # Integration tests
task test:property      # Property-based tests (Hypothesis)
task test:performance   # Performance benchmarks
task test:e2e           # Backend end-to-end tests
task test:e2e:frontend  # Frontend Playwright end-to-end tests
task test:frontend      # Frontend tests (Vitest)

# Coverage
task test:coverage      # With coverage report

# Direct frontend Playwright
cd frontend && bun run test:e2e
```

### Test Organization

```text
tests/
├── unit/           # Fast, isolated, no I/O
├── integration/    # Database, API, external services
├── property/       # Hypothesis property-based tests
├── performance/    # Benchmark tests
├── e2e/            # End-to-end tests
├── fixtures/       # Shared test data
├── factories/      # factory-boy factories
└── mocks/          # Reusable mocks
```

### Container-backed Integration/E2E Notes

- Backend integration and selected E2E API tests run against PostgreSQL via `testcontainers`.
- Docker must be available locally for these container-backed scenarios.
- If Docker is unavailable, those containerized tests are skipped automatically.

Backend API e2e quick commands:

```bash
# Repository-level containerized backend e2e
uv run --project backend python -m pytest tests/e2e -q

# Backend-local e2e
cd backend && uv run python -m pytest tests/e2e -q
```

## 📝 Code Quality

### Linting

```bash
task lint              # All linters
task lint:python       # Python (ruff)
task lint:frontend     # Frontend (biome)
task lint:yaml         # YAML files
task lint:markdown     # Markdown files
task lint:secrets      # Secret scanning
```

### Formatting

```bash
task format            # Format all code
```

### Type Checking

```bash
task typecheck         # Python (mypy) + Frontend (tsc)
```

### Complexity

```bash
task xenon             # Cyclomatic complexity check
```

### Pre-commit Hooks

```bash
# Run all pre-commit hooks
task pre-commit

# Install hooks (automatic with task install)
cd backend && uv run pre-commit install
```

## 🗄️ Database

### Migrations

```bash
# Run pending migrations
task db:migrate

# Create new migration
cd backend
uv run alembic revision --autogenerate -m "description"

# Rollback
task db:downgrade

# Reset database
task db:reset
```

## 📦 Building

### Standalone EXE

```bash
# Build with PyInstaller
task build:exe

# Output: dist/ekko/ekko.exe
```

### Frontend

```bash
# Build optimized frontend
cd frontend && bun run build

# Preview production build
cd frontend && bun run preview
```

## 🔐 Security

### Secret Scanning

```bash
# Scan for secrets
task lint:secrets

# Update baseline
cd backend && uv run detect-secrets scan --update .secrets.baseline
```

### Dependency Audits

```bash
# Audit Python dependencies
task security:audit
```

### Pre-commit Hooks

Automatic security checks:

- detect-secrets
- gitleaks
- bandit (Python security)

## 🐳 Devcontainer

Open in VS Code and choose "Reopen in Container".

Features:

- Pre-configured Python + Node environment
- All tools installed
- VS Code extensions pre-installed
- Ready to code immediately

## 🐳 Docker + Caddy (Local)

Ekko includes a local container stack for backend runtime plus optional HTTPS reverse proxy.

```bash
# Backend container only
docker compose -f docker/compose.yaml -f docker/compose.override.yaml up --build

# Backend + local HTTPS reverse proxy (Caddy)
docker compose -f docker/compose.yaml -f docker/compose.override.yaml --profile caddy up --build
```

Key files:

- `docker/Containerfile`
- `docker/compose.yaml`
- `docker/compose.override.yaml`
- `caddy/Caddyfile`

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

Quick overview:

1. Fork the repository
2. Create feature branch (`feature/your-feature`)
3. Follow coding conventions
4. Write tests
5. Run `task check`
6. Submit pull request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- CrewAI for multi-agent orchestration
- React team for React 19
- shadcn for the beautiful UI components
- All open source contributors

## 📞 Support

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **Email**: <lfr@tik-ai.dk>

---

**Made with ❤️ using Clean Architecture principles**
