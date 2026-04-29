# Ekko

AI-powered voice assistant platform with CrewAI agents, GraphQL, and PII anonymization.

## Quickstart

1. Install dependencies:

```bash
uv sync --all-extras
cd frontend && bun install
```

2. Run locally:

```bash
task dev
```

3. Run tests:

```bash
task check
```

## Devcontainer

Open in VS Code and choose "Reopen in Container". The dev container provisions
the `uv` toolchain, pre-commit tooling, Bun, and VS Code settings/extensions.

## Architecture

Clean Architecture with strict dependency direction:
`presentation/infrastructure → application → core`

- **Backend**: FastAPI, Strawberry GraphQL, CrewAI, SQLAlchemy, PostgreSQL
- **Frontend**: React 19, Vite, Tailwind, shadcn, Storybook
- **Infra**: Caddy reverse proxy, Docker Compose, Alembic migrations
- **AI**: CrewAI HMAS agents, PII anonymization before LLM calls

## CI

GitHub Actions workflow runs:
- Pre-commit hooks
- Type checking (mypy)
- Unit, integration, and property-based tests
- Architecture boundary checks
- Security scanning
