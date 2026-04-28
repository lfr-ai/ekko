# Developer README

This guide describes the local developer workflow for `voice-bot`.

## Setup

1. Install dependencies with uv (recommended):
	 - `uv sync --all-extras`

2. Optional: use the dev container:
	 - Open in VS Code and run **Dev Containers: Reopen in Container**.

## Daily Commands

- Start app: `task dev`
- Run tests: `task test`
- Run integration tests: `task test:integration`
- Lint/type checks: `task lint`
- Run all hooks: `task precommit`
- Full quality gate: `task check`

## Development

Recommended developer setup:

This repository originally used PDM. Astral's `uv` is the recommended project
toolchain (package/runtime manager). To migrate, run `scripts/migrate_to_uv.sh`.

Below
are both options; pick one and be consistent across your environment.


- Using uv (recommended):
	- Install deps: `uv sync --all-extras`
	- Run hooks: `uvx pre-commit run --all-files`
	- Run tests: `uvx pytest -q`

- Using uv (alternative — Astral uv):
	- Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
	- Sync deps: `uv sync --all-groups`
	- Install pre-commit: `uvx pipx run pre-commit install` or follow `scripts/bootstrap-uv.sh`
	- Run tests: `uvx pytest -q` or `uv run pytest -q`

Devcontainer: open repository in VS Code and reopen in container to get consistent dev environment.

## Quality and Security Tooling

- `pre-commit` hooks include Ruff, mypy, Bandit, detect-secrets, typos, and yamllint.
- Clean Architecture boundaries are checked by:
	- CI workflow (`.github/workflows/ci.yml`)
	- Local script (`scripts/check_architecture_boundaries.py`)
- Supporting policy/config files include:
	- `.editorconfig`, `.yamllint.yaml`, `.markdownlint-cli2.yaml`, `.typos.toml`
	- `.lychee.toml`, `.hadolint.yaml`, `.secrets.baseline`

## Container Workflows

- Dev container config: `.devcontainer/`
- Compose matrix: `docker/compose.yml` + environment overrides in `docker/compose.*.yml`
