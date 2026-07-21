#!/usr/bin/env sh
set -eu

if [ "${SKIP_TOOL_GUARD:-}" = "true" ]; then
  exit 0
fi

GUARD_MODE="${GUARD_MODE:-block}"
LOG_DIR="${TOOL_GUARD_LOG_DIR:-logs/copilot/tool-guardian}"
mkdir -p "${LOG_DIR}"

INPUT="$(cat)"
SCAN_TEXT="${INPUT}"

if printf '%s' "${SCAN_TEXT}" | grep -qiE 'rm[[:space:]]+-r[[:space:]]*f?[[:space:]]*/|git[[:space:]]+push[[:space:]]+--force|DROP[[:space:]]+DATABASE|curl[[:space:]].*\|[[:space:]]*bash'; then
  printf '{"timestamp":"%s","event":"threats_detected","mode":"%s"}\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${GUARD_MODE}" >> "${LOG_DIR}/guard.log"
  if [ "${GUARD_MODE}" = "block" ]; then
    printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Tool Guardian: potentially destructive command detected"}}'
    exit 2
  fi
fi

printf '{"timestamp":"%s","event":"guard_passed","mode":"%s"}\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${GUARD_MODE}" >> "${LOG_DIR}/guard.log"
