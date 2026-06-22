---
name: openspec-ff-change
description: Fast-forward through OpenSpec artifact creation. Use when the user wants to quickly create all artifacts needed for implementation without stepping through each one individually.
license: MIT
compatibility: Requires openspec CLI.
metadata:
  author: openspec
  version: "1.0"
  generatedBy: "1.4.1"
---

Fast-forward through artifact creation and generate everything required to start implementation.

Core flow:
1. Create/select change
2. Read status for artifact ordering and apply requirements
3. Iteratively create all `ready` artifacts
4. Stop when all apply-required artifacts are `done`
5. Show final status and hand off to `/opsx:apply`

Guardrails:
- Preserve dependency order
- Ask user only when critical context is missing
- Ensure all apply-required artifacts are created
