---
paths:
  - "memories/**/*.md"
---

# Memory write discipline

`memories/` is committed, provider-neutral, cross-session agent context. Follow
`memories/README.md` for the read order and the `self-reflection` skill for when
to record. These rules always apply when editing a memory file.

## What belongs here

- A verified fact, a durable agent-development decision, a recurring lesson
  (a gotcha plus its recovery), or an unfinished-work handoff — nothing else.
- Never: private reasoning, transcripts, secrets, generated inventories, or
  speculative "might need this later" notes.

## How to write it

- Record only when a verified fact, decision, lesson, or handoff actually
  changed. Do not log routine, one-off task outcomes.
- Include evidence: a file path, a command, a check, or an authoritative URL.
- Keep each entry short. If a topic needs a guide, put it in docs/specs and link
  it from here instead of inlining it.
- Do not duplicate what `AGENTS.md`, `PROJECT.md`, an instruction, or a skill
  already states — link to the source of truth.
- Remove stale entries in the same change; a note citing a moved or deleted file
  is itself stale (the `self-reflection` skill bundles a freshness checker).

## Consolidate before you append

- `lessons.md`/`decisions.md` are guard-enforced at a 500-line budget
  (`_MEMORY_LOG_LINE_BUDGET`). Before adding an entry, check whether an
  existing one already covers the same evolving topic — merge into it instead
  of stacking a new one.
- Once a file is near budget, move fully-resolved incident narratives (fix
  already reflected in code/skills) to `memories/archive/<file>.md` verbatim,
  leaving a short pointer behind. Never raise the budget to fit new content.

## Handoffs

- One parallel agent writes one `handoffs/YYYY-MM-DD-<task>-<agent>.md`; never
  share an in-progress handoff file.
- Fold a completed task's durable facts into `project.md` / `decisions.md` /
  `lessons.md` and delete its obsolete handoff.

## Fixing the setup

- If the surprise reveals the agentic setup itself is wrong, fix it under the
  `agent-config` skill's placement rules and record the *why* in `decisions.md` —
  the fix and its reason travel together.
