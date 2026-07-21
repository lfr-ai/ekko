#!/usr/bin/env bash
# License Checker — Stop hook (Unix)
# Scans dependencies for copyleft or unapproved licenses.
set -euo pipefail

LICENSE_MODE="${LICENSE_MODE:-warn}"
LOG_DIR="${LICENSE_LOG_DIR:-logs/copilot/license-checker}"
mkdir -p "$LOG_DIR"

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

BLOCKED_LICENSES=(
    "GPL-2.0"
    "GPL-3.0"
    "AGPL-3.0"
    "LGPL-2.1"
    "LGPL-3.0"
    "MPL-2.0"
    "EUPL-1.2"
    "SSPL-1.0"
    "CC-BY-SA-4.0"
)

VIOLATIONS=0

# Check frontend dependencies
if [[ -d "frontend" ]] && command -v npx &>/dev/null; then
    LICENSE_OUTPUT=$(npx license-checker --json --start frontend 2>/dev/null || true)
    if [[ -n "$LICENSE_OUTPUT" ]]; then
        for blocked in "${BLOCKED_LICENSES[@]}"; do
            COUNT=$(echo "$LICENSE_OUTPUT" | grep -c "\"$blocked\"" 2>/dev/null || true)
            VIOLATIONS=$((VIOLATIONS + COUNT))
        done
    fi
fi

if [[ $VIOLATIONS -gt 0 ]]; then
    echo "{\"timestamp\":\"$TIMESTAMP\",\"event\":\"license_violations\",\"mode\":\"$LICENSE_MODE\",\"count\":$VIOLATIONS}" >> "$LOG_DIR/license.log"

    if [[ "$LICENSE_MODE" == "block" ]]; then
        echo "License Checker: $VIOLATIONS copyleft/unapproved license(s) detected" >&2
        exit 1
    else
        echo "{\"systemMessage\":\"License Checker: $VIOLATIONS license concern(s) found (warn mode)\"}"
        exit 0
    fi
else
    echo "{\"timestamp\":\"$TIMESTAMP\",\"event\":\"license_check_passed\",\"mode\":\"$LICENSE_MODE\"}" >> "$LOG_DIR/license.log"
    exit 0
fi
