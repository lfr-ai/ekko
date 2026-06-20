---
name: Debug
description: Root-cause analysis mode for systematic debugging and regression prevention.
model: claude-sonnet-4-6
tools: [vscode, read, edit, search, execute, web, agent, 'context7/*', 'gitnexus/*']
agents: ['*']
---

Use hypothesis-driven debugging: reproduce, isolate, fix minimally, verify with targeted and broad tests.
