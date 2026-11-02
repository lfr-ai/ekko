---
name: self-reflection
description: Capture a lesson, decision, or agentic-setup gap the moment it surfaces — after a bug caused by a wrong assumption, a user correction, repeated friction, or a stale/missing skill, instruction, rule, or MCP entry — so it is recorded once instead of relearned. Use when a task revealed a non-obvious gotcha, when corrected twice on the same point, or when the agentic setup itself is found stale or inconsistent.
---

# Self-reflection and memory upkeep

Treat every genuine surprise as a signal to record, not just move past. A
surprise is: a wrong assumption that cost rework, a user correction, a
repeated question, a stale doc, or a governance gap (missing skill,
instruction, rule, or MCP entry) discovered mid-task.

## Trigger checklist

Pause and reflect when any of these happen:

- You were wrong about how the codebase, a tool, or a convention worked, and
  it cost a retry or a wasted edit.
- The user corrected you, or repeated an instruction already given earlier in
  the project's history.
- You discovered the agentic setup itself (a skill, instruction, rule, MCP
  entry, or guard rule) is missing, stale, or contradicts another part of it.
- A task succeeded only after a non-obvious workaround (environment quirk,
  ordering requirement, tool limitation).

Do **not** log routine, one-off task outcomes, or anything already covered by
an existing memory entry, instruction, or skill — only what would otherwise be
relearned the hard way next time.

## Where to record it

Follow the `agent-config` skill's table for skill/instruction/rule placement.
For memory specifically:

| Scope | Location | Use for |
| --- | --- | --- |
| This session only | Session memory (`/memories/session/`) | In-progress task state, not durable |
| This repo, durable | [`memories/lessons.md`](../../../memories/lessons.md) / [`memories/decisions.md`](../../../memories/decisions.md) (committed) | Gotchas, verified facts, agent-dev decisions any agent should know |
| This repo, agent tool | `/memories/repo/*.md` (agent memory tool) | Same as above, on a memory-tool-backed runtime |
| Any repo (this user) | User memory (`/memories/*.md`) | Preferences and patterns that generalize beyond this repo |

See [`memories/README.md`](../../../memories/README.md) for the write rules:
include evidence (file, command, or authoritative source), remove stale
entries in the same change, and keep each entry short.

## Consolidate, don't just append

`memories/lessons.md` and `memories/decisions.md` are guard-enforced at a
500-line budget (`_MEMORY_LOG_LINE_BUDGET` in `verify_agent_config.py`) —
unlike a frozen policy-file ceiling, exceeding it means *consolidate*, not
trim: before writing a new entry, check whether an existing one already
covers the same evolving topic (three or more sessions re-deriving the same
convention is the clearest signal) and merge into it instead of stacking a
new one. Once a file is at or near budget, move any entry whose fix is
already reflected in code/skills to `memories/archive/<file>.md` verbatim,
leaving a short pointer behind — never delete it outright, and never raise
the budget to make room.

## If the gap is in the agentic setup itself

When the surprise reveals the setup is wrong — not just the codebase — fix it
in the same change-set using the `agent-config` skill's placement rules,
verify with `.agents/guard/verify_agent_config.py`, and only then record the
decision in `memories/decisions.md`. The fix and the record of *why* travel
together; a fix without a recorded reason lets the next agent re-discover and
re-litigate the same gap.

## Anti-patterns

- Recording something already in `AGENTS.md`, an instruction file, or an
  existing memory entry — that is duplication, not learning.
- Writing private reasoning, transcripts, or speculative notes instead of a
  verified fact or decision.
- Fixing the setup without recording why, or recording a lesson without fixing
  the setup it exposes.

## Templates and references

- [`assets/memory-entry.template.md`](assets/memory-entry.template.md) — the
  one-entry shape to copy, with a bug-fix example and a governance-gap example.
- [`scripts/check_memory_freshness.py`](scripts/check_memory_freshness.py) —
  read-only scan of a memory file for backtick/markdown-link paths that no
  longer exist on disk (a memory note citing a moved/deleted file is a stale
  note). Run periodically, e.g.:
  `uv run python scripts/check_memory_freshness.py memories/lessons.md memories/decisions.md`.
