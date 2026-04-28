#!/usr/bin/env bash
set -euo pipefail

echo "Migrating project to Astral 'uv' toolchain (interactive)."

if ! command -v uv >/dev/null 2>&1; then
  echo "uv not found. Installing uv (astral) via their installer..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$HOME/.uv/bin:$PATH"
fi

echo "Running uv sync to install dependencies and produce uv.lock"
# Sync will create/refresh uv.lock
uv sync --all-extras

if [ -f uv.lock ]; then
  echo "uv.lock created. Add and commit it to your repo to pin dependencies."
  echo "  git add uv.lock && git commit -m 'chore: add uv.lock (migrate to uv)'"
else
  echo "No uv.lock found. Inspect uv output and run 'uv lock' or 'uv sync --lock' if desired."
fi

echo "You may also want to update your local dev container and CI to use 'uv' (already attempted by this repo)."

echo "Migration complete. Run 'uvx pre-commit run --all-files' to ensure hooks run under uvx."