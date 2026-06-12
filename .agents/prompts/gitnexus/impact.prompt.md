---
description: Investigate impact concerns with GitNexus and summarize blast radius before edits.
---

Use GitNexus to perform **impact** analysis before implementing changes.

Required behavior:

1. Find relevant symbols/processes with `mcp_gitnexus_query`.
2. Inspect critical symbols with `mcp_gitnexus_context`.
3. Assess risk using `mcp_gitnexus_impact` for touched symbols.
4. Summarize impacted modules/processes and recommended safe change order.
5. If risk is HIGH/CRITICAL, propose staged rollout with validation checkpoints.
