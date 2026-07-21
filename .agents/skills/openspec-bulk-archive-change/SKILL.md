---
name: openspec-bulk-archive-change
description: Archive multiple completed changes at once. Use when archiving several parallel changes.
license: MIT
compatibility: Requires openspec CLI.
metadata:
  author: openspec
  version: "1.0"
  generatedBy: "1.4.1"
---

Archive multiple changes in one operation.

Core flow:
1. List active changes
2. Ask user for multi-select
3. Validate artifact/task readiness per change
4. Detect delta spec conflicts across selected changes
5. Resolve conflicts using codebase evidence
6. Sync specs where required
7. Archive each change with dated folder naming
8. Report success/skipped/failed outcomes

Guardrails:
- Never auto-select changes
- Continue archiving others if one change fails
- Always show conflict resolution rationale
