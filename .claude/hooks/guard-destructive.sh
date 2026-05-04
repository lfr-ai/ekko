#!/usr/bin/env bash
# Guard Destructive Commands — PreToolUse hook (Unix)
set -euo pipefail

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [ -z "$COMMAND" ]; then
  exit 0
fi

if echo "$COMMAND" | grep -qEi 'rm\s+-r\s*f?\s*/|git\s+push\s+--force|git\s+reset\s+--hard|git\s+clean\s+-fd|DROP\s+(DATABASE|TABLE)|curl\s+.*\|\s*(ba)?sh|wget\s+.*\|\s*(ba)?sh|chmod\s+777|mkfs\.|:>\s*/'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "Blocked by guard-destructive hook: potentially destructive command detected"
    }
  }'
  exit 2
fi

exit 0
