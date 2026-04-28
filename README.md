# voice-bot

Opinionated developer guide

Quickstart

1. Create and activate a virtual environment, then install runtime and dev dependencies:

   ```bash
   python -m venv .venv
   # Windows
   .\.venv\Scripts\activate
   # macOS / Linux
   source .venv/bin/activate

   python -m pip install --upgrade pip
   pip install -r requirements.txt
   pip install -r requirements-dev.txt || pip install -e .[dev]
   ```

2. Run locally (uvicorn):

   ```bash
   make run
   # or
   uvicorn voice.interaction.main:app --reload
   ```

Devcontainer

Open in VS Code and choose "Reopen in Container". The dev container provisions
the `uv` toolchain, pre-commit tooling, and VS Code settings/extensions automatically.

CI

A GitHub Actions workflow runs:

- pre-commit hooks
- mypy type-checking
- tests
- clean architecture import boundary checks
- markdown link checks
- shell script linting

Developer quickstart

1. Create a virtual environment and install dev deps:

```bash
python -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -e .[dev]
```

1. Run linters and tests:

```bash
task check
```

1. Run the app locally:

```bash
uvicorn voice.interaction.main:app --reload
```
