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
  is itself stale.

## Handoffs

- One parallel agent writes one `handoffs/YYYY-MM-DD-<task>-<agent>.md`; never
  share an in-progress handoff file.
- Fold a completed task's durable facts into `decisions.md` / `lessons.md` and
  delete its obsolete handoff.

## Fixing the setup

- If the surprise reveals the agentic setup itself is wrong, fix it under the
  `agent-config` skill's placement rules in the same change, then record the
  decision here — see the `self-reflection` skill.
