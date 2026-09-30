---
name: "GitNexus: Impact Analysis"
description: Run impact workflow with GitNexus before code changes.
category: Analysis
tags: [gitnexus, architecture, risk]
---

Run a GitNexus **impact** workflow:

1. Start with `gitnexus_query` for semantic process discovery.
2. Use `gitnexus_context` on top candidate symbols.
3. Run `gitnexus_impact` upstream with depth 2-3 for blast radius.
4. Return findings grouped as: direct impact, transitive impact, test priorities.
5. Recommend the safest incremental refactoring sequence.
