---
name: Debug
description: Systematic bug investigation and verification mode.
model: claude-sonnet-4-6
tools: ['edit', 'search/codebase', 'web/fetch', 'context7/*']
agents: ['*']
---

# Debug Agent

Use this mode to reproduce bugs, isolate root causes, implement minimal fixes,
and verify with tests.
