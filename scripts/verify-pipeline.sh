#!/usr/bin/env bash
# Pre-push verification script for Ekko (Unix)
# Usage: ./scripts/verify-pipeline.sh

set -euo pipefail

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

step() {
  echo ""
  echo -e "${BLUE}=== $1 ===${NC}"
}

ok() {
  echo -e "${GREEN}[ok]${NC} $1"
}

warn() {
  echo -e "${YELLOW}[warn]${NC} $1"
}

if ! command -v task >/dev/null 2>&1; then
  echo "task command not found. Install Task from https://taskfile.dev/"
  exit 1
fi

step "Formatting checks"
( cd backend && uv run ruff format --check src tests )
( cd frontend && bun run lint )
ok "Formatting/lint checks completed"

step "Type checks"
( cd backend && uv run ty check src/ekko )
( cd frontend && bun run typecheck )
ok "Type checks completed"

step "Tests"
( cd backend && uv run pytest tests/unit -q )
( cd frontend && bun run test )
ok "Unit tests completed"

step "Build"
( cd frontend && bun run build )
ok "Frontend build completed"

step "Workflow lint (optional local)"
if command -v actionlint >/dev/null 2>&1; then
  actionlint -color
  ok "actionlint completed"
else
  warn "actionlint not installed locally; CI workflow validates this"
fi

echo ""
echo -e "${GREEN}Pipeline verification completed successfully.${NC}"
