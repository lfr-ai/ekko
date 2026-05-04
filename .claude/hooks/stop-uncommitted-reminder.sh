#!/usr/bin/env bash
# Uncommitted Files Reminder — Stop hook (Unix)
# Outputs a systemMessage JSON reminder when uncommitted files exist.
set -euo pipefail

STATUS=$(git status --porcelain 2>/dev/null || true)
if [ -z "$STATUS" ]; then
  exit 0
fi

COUNT=$(echo "$STATUS" | wc -l | tr -d ' ')
jq -n --arg msg "Reminder: $COUNT uncommitted file(s) in working tree." \
  '{ systemMessage: $msg }'
exit 0
