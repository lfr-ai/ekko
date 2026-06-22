---
name: openspec-verify-change
description: Verify implementation matches change artifacts. Use when the user wants to validate that implementation is complete, correct, and coherent before archiving.
license: MIT
compatibility: Requires openspec CLI.
metadata:
  author: openspec
  version: "1.0"
  generatedBy: "1.4.1"
---

Verify implementation against artifacts with three dimensions:

1. Completeness (tasks + requirement coverage)
2. Correctness (spec/scenario alignment)
3. Coherence (design and pattern consistency)

Output severity buckets:
- CRITICAL (must fix)
- WARNING (should fix)
- SUGGESTION (nice to improve)

Guardrails:
- Base findings on artifact and code evidence
- Prefer actionable findings with file references
- Distinguish uncertainty from confirmed gaps
