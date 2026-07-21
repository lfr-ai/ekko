---
name: openspec-continue-change
description: Continue working on an OpenSpec change by creating the next artifact. Use when the user wants to progress their change, create the next artifact, or continue their workflow.
license: MIT
compatibility: Requires openspec CLI.
metadata:
  author: openspec
  version: "1.0"
  generatedBy: "1.4.1"
---

Continue working on a change by creating the next artifact.

Core flow:
1. Select change (`openspec list --json` if needed)
2. Check status (`openspec status --change "<name>" --json`)
3. Pick first artifact with `status: "ready"`
4. Load instructions (`openspec instructions <artifact-id> --change "<name>" --json`)
5. Create exactly one artifact
6. Show progress and next unlocked artifacts

Guardrails:
- Create ONE artifact per invocation
- Never skip artifact dependency order
- Read dependency artifacts before creating the next artifact
