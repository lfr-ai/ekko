# Development setup

This document describes how to prepare a development environment for the
project and the recommended commands for common tasks.

## Requirements

- Python 3.11+
- A system package manager (apt / brew / choco) for optional native deps
- Node.js / Bun for frontend (optional)

## Recommended workflow

1. Install dependencies (uv preferred):

```bash
uv sync --all-extras
```

1. Create a local `.env` file (copy `.env.example`) and adjust values.

1. Create the database and run migrations:

```bash
uv run alembic upgrade head
```

1. Run tests:

```bash
uv run pytest -q
```
