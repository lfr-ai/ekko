#!/usr/bin/env bash
#
# Pre-push verification script for Ekko
# Runs all checks that would run in CI/CD pipeline
#
# Usage: ./scripts/verify-pipeline.sh
# Or: task verify

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Track failures
FAILED=0

print_header() {
    echo ""
    echo -e "${BOLD}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}  $1${NC}"
    echo -e "${BOLD}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
    FAILED=$((FAILED + 1))
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

run_check() {
    local name=$1
    shift
    echo -e "${BOLD}Running: ${name}${NC}"
    if "$@"; then
        print_success "$name passed"
        return 0
    else
        print_error "$name failed"
        return 1
    fi
}

# ═══════════════════════════════════════════════════════════════════════════
# Main verification
# ═══════════════════════════════════════════════════════════════════════════

print_header "🔍 Ekko Pipeline Verification"

echo "This script will run all checks that would run in CI/CD."
echo "It may take several minutes to complete."
echo ""

# Check if task is available
if ! command -v task &> /dev/null; then
    print_error "task command not found. Please install Task: https://taskfile.dev/"
    exit 1
fi

# ─────────────────────────────────────────────────────────────────────────────
# 1. Code Formatting
# ─────────────────────────────────────────────────────────────────────────────

print_header "1️⃣  Code Formatting"

run_check "Backend formatting (ruff)" \
    bash -c "cd backend && uv run ruff format --check ." || true

run_check "Frontend formatting (biome)" \
    bash -c "cd frontend && bunx biome format --check ." || true

# ─────────────────────────────────────────────────────────────────────────────
# 2. Linting
# ─────────────────────────────────────────────────────────────────────────────

print_header "2️⃣  Linting"

run_check "Backend linting (ruff)" \
    bash -c "cd backend && uv run ruff check ." || true

run_check "Frontend linting (biome)" \
    bash -c "cd frontend && bun run biome check ." || true

run_check "YAML linting" \
    yamllint -c .yamllint.yaml . || true

run_check "Spelling check (typos)" \
    typos . || true

# ─────────────────────────────────────────────────────────────────────────────
# 3. Type Checking
# ─────────────────────────────────────────────────────────────────────────────

print_header "3️⃣  Type Checking"

run_check "Backend type checking (mypy)" \
    bash -c "cd backend && uv run mypy --config-file mypy.ini src/" || true

run_check "Frontend type checking (tsc)" \
    bash -c "cd frontend && bun run typecheck" || true

# ─────────────────────────────────────────────────────────────────────────────
# 4. Security Checks
# ─────────────────────────────────────────────────────────────────────────────

print_header "4️⃣  Security Checks"

run_check "Secret scanning (detect-secrets)" \
    bash -c "cd backend && uv run detect-secrets scan --baseline ../.secrets.baseline" || true

run_check "Security analysis (bandit)" \
    bash -c "cd backend && uv run bandit -c ../bandit.toml -r src/" || true

# ─────────────────────────────────────────────────────────────────────────────
# 5. Code Complexity
# ─────────────────────────────────────────────────────────────────────────────

print_header "5️⃣  Code Complexity"

run_check "Cyclomatic complexity (xenon)" \
    bash -c "cd backend && uv run xenon --max-absolute B --max-modules B --max-average A src/" || true

# ─────────────────────────────────────────────────────────────────────────────
# 6. Testing
# ─────────────────────────────────────────────────────────────────────────────

print_header "6️⃣  Testing"

run_check "Backend unit tests" \
    bash -c "cd backend && uv run pytest tests/unit -v" || true

run_check "Backend integration tests" \
    bash -c "cd backend && uv run pytest tests/integration -v" || true

run_check "Frontend tests" \
    bash -c "cd frontend && bun run test" || true

# ─────────────────────────────────────────────────────────────────────────────
# 7. Coverage
# ─────────────────────────────────────────────────────────────────────────────

print_header "7️⃣  Test Coverage"

run_check "Backend coverage (min 70%)" \
    bash -c "cd backend && uv run pytest --cov=src/ekko --cov-report=term --cov-fail-under=70" || true

# ─────────────────────────────────────────────────────────────────────────────
# 8. Build
# ─────────────────────────────────────────────────────────────────────────────

print_header "8️⃣  Build Verification"

run_check "Frontend build" \
    bash -c "cd frontend && bun run build" || true

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────

print_header "📊 Verification Summary"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}${BOLD}✓ All checks passed!${NC}"
    echo ""
    echo "✅ Pipeline will likely pass"
    echo "You can safely commit and push your changes."
    echo ""
    exit 0
else
    echo -e "${RED}${BOLD}✗ $FAILED check(s) failed${NC}"
    echo ""
    echo "❌ Pipeline will likely fail"
    echo "Please fix the issues above before committing."
    echo ""
    echo "Tip: Run 'task format' to auto-fix formatting issues"
    echo "Tip: Run 'task lint' to see detailed linting errors"
    echo ""
    exit 1
fi
