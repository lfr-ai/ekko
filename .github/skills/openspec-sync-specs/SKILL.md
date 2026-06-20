---
name: openspec-sync-specs
description: Sync delta specs from a change to main specs. Use when the user wants to update main specs with changes from a delta spec, without archiving the change.
license: MIT
compatibility: Requires openspec CLI.
metadata:
  author: openspec
  version: "1.0"
  generatedBy: "1.4.1"
---

Sync delta specs from a change into `openspec/specs/` using intelligent merging.

Core flow:
1. Select change
2. Resolve status and artifact paths
3. Read delta specs under change scope
4. Apply ADDED/MODIFIED/REMOVED/RENAMED requirements to main specs
5. Preserve unchanged scenarios/content
6. Report synced capabilities and requirement changes

Guardrails:
- Never blindly overwrite main specs
- Merge intent, not file blobs
- Keep operation idempotent
