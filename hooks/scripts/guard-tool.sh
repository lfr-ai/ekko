#!/usr/bin/env bash
# Tool Guardian — PreToolUse hook (Unix)
# Blocks dangerous tool operations before the Copilot coding agent executes them.
# Enforces repository rule that agents never run git shell commands.
set -euo pipefail

[[ "${SKIP_TOOL_GUARD:-}" == "true" ]] && exit 0

GUARD_MODE="${GUARD_MODE:-block}"
LOG_DIR="${TOOL_GUARD_LOG_DIR:-logs/copilot/tool-guardian}"
mkdir -p "$LOG_DIR"

INPUT_JSON=$(cat)
TOOL_NAME=$(echo "$INPUT_JSON" | jq -r '.tool_name // empty' 2>/dev/null || true)
TOOL_INPUT=$(echo "$INPUT_JSON" | jq -r '.tool_input // empty' 2>/dev/null || true)
SCAN_TEXT="$TOOL_NAME $TOOL_INPUT"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

IS_COMMAND_TOOL=false
if [[ "$TOOL_NAME" == "run_in_terminal" || "$TOOL_NAME" == "Bash" ]]; then
    IS_COMMAND_TOOL=true
fi

THREATS=()

# Repository policy: agents must never run git commands
if [[ "$IS_COMMAND_TOOL" == "true" ]] && echo "$TOOL_INPUT" | grep -qP '\bgit(\.exe)?\s+'; then
    THREATS+=("git_operations_blocked:critical:git:Git commands are disabled for agents")
fi

# Destructive patterns
declare -a PATTERNS=(
    "rm\s+-r\s*f?\s*/(\s|$):critical:destructive_file_ops"
    "rm\s+-r\s*f?\s*~:critical:destructive_file_ops"
    "git\s+push\s+--force\s+(origin\s+)?(main|master):critical:destructive_git_ops"
    "git\s+reset\s+--hard:high:destructive_git_ops"
    "DROP\s+DATABASE:critical:database_destruction"
    "DROP\s+TABLE:critical:database_destruction"
    "curl\s+.*\|\s*bash:critical:network_exfiltration"
    "wget\s+.*\|\s*sh:critical:network_exfiltration"
    "sudo\s+:high:system_danger"
)

for pattern_entry in "${PATTERNS[@]}"; do
    IFS=':' read -r regex severity category <<< "$pattern_entry"
    if echo "$SCAN_TEXT" | grep -qP "$regex" 2>/dev/null; then
        THREATS+=("$category:$severity:$regex:Blocked by tool guardian")
    fi
done

if [[ ${#THREATS[@]} -gt 0 ]]; then
    echo "{\"timestamp\":\"$TIMESTAMP\",\"event\":\"threats_detected\",\"mode\":\"$GUARD_MODE\",\"tool\":\"$TOOL_NAME\",\"threat_count\":${#THREATS[@]}}" >> "$LOG_DIR/guard.log"

    if [[ "$GUARD_MODE" == "block" ]]; then
        REASON="Tool Guardian: ${#THREATS[@]} threat(s) detected"
        echo "{\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"permissionDecision\":\"deny\",\"permissionDecisionReason\":\"$REASON\"}}"
        exit 2
    else
        echo "{\"systemMessage\":\"Tool Guardian: ${#THREATS[@]} threat(s) detected (warn mode)\"}"
        exit 0
    fi
else
    echo "{\"timestamp\":\"$TIMESTAMP\",\"event\":\"guard_passed\",\"mode\":\"$GUARD_MODE\",\"tool\":\"$TOOL_NAME\"}" >> "$LOG_DIR/guard.log"
    exit 0
fi
