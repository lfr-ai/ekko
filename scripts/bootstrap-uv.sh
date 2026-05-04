#!/usr/bin/env bash
set -euo pipefail

# Bootstrap script for 'uv' users. Installs dependencies and pre-commit.
# Requires: uv (https://astral.sh/uv)

echo "Bootstrapping project with uv..."
if ! command -v uv >/dev/null 2>&1; then
  echo "uv not found. Please install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
  exit 1
fi

echo "Syncing dependencies..."
uv sync --all-groups

echo "Installing pre-commit hooks..."
uvx pre-commit install || true

echo "Bootstrap complete. Run 'uv run pytest -q' to run tests."
