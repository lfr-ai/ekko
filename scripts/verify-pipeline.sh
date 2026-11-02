#!/usr/bin/env bash
# Pre-push verification script for Ekko (Unix)
# Usage: ./scripts/verify-pipeline.sh [--full]
#
# Default mode: fast checks (< 5 min)
#   - Formatting, linting
#   - Type checking
#   - Unit tests
#   - Build verification
#
# Full mode (--full): complete CI mirror (~10-15 min)
#   - All default checks PLUS
#   - Security scans (bandit, pip-audit, detect-secrets)
#   - Integration tests
#   - Architecture boundary checks

set -euo pipefail

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

FULL_MODE=false

# Parse arguments
if [[ "${1:-}" == "--full" ]]; then
  FULL_MODE=true
elif [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  echo "Usage: $0 [--full]"
  echo ""
  echo "Default: Run fast pre-push checks (formatting, types, unit tests)"
  echo "--full:  Run complete CI mirror including security scans and integration tests"
  exit 0
fi

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

# ============================================================================
# Default mode: Fast checks
# ============================================================================

step "Formatting checks"
( cd backend && uv run ruff format --check src tests )
( cd frontend && bun run lint )
ok "Formatting/lint checks completed"

step "Type checks"
( cd backend && uv run python -m ty check src/ekko tests ../tests ../tools ../scripts ../registry alembic )
( cd frontend && bun run typecheck )
ok "Type checks completed"

step "Unit tests"
( cd backend && uv run python -m pytest tests/unit -q )
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

# ============================================================================
# Full mode: Additional CI checks
# ============================================================================

if [[ "$FULL_MODE" == true ]]; then
  echo ""
  echo -e "${BLUE}=== Running full CI mirror mode ===${NC}"

  step "Security: Bandit"
  ( cd backend && uv run python -m bandit -c bandit.toml -r src )
  ok "Bandit scan completed"

  step "Security: pip-audit"
  uv run --project backend python scripts/security/dependency_audit.py
  ok "pip-audit scan completed"

  step "Security: detect-secrets"
  ( cd backend && uv run detect-secrets scan --baseline ../.secrets.baseline )
  ok "detect-secrets scan completed"

  step "Integration tests"
  ( cd backend && uv run python -m pytest tests/integration -q -m integration )
  ok "Integration tests completed"

  step "Architecture: Clean Architecture boundaries"
  uv run --project backend python tools/security/check_architecture_boundaries.py
  ok "Clean Architecture import boundaries verified"
fi

# ============================================================================
# Done
# ============================================================================

echo ""
if [[ "$FULL_MODE" == true ]]; then
  echo -e "${GREEN}Full pipeline verification completed successfully.${NC}"
else
  echo -e "${GREEN}Pipeline verification completed successfully.${NC}"
  echo -e "${YELLOW}Tip: Run with --full to include security scans and integration tests${NC}"
fi
