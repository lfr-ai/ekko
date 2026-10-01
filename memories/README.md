# Shared agent memory

Committed, provider-neutral context for agents working in this repository.
Store verified outcomes and reusable facts — not private reasoning, secrets,
transcripts, generated inventories, or speculative notes.

## Read order

1. [`decisions.md`](decisions.md) — durable agent-development decisions.
2. [`lessons.md`](lessons.md) — proven gotchas and recoveries relevant to the task.
3. [`handoffs/`](handoffs/) — recent unfinished-work summaries; read only relevant files.

`PROJECT.md` remains the source of project facts, `openspec/specs/` owns
behavior, and `.agents/knowledge-base/` owns architecture/domain synthesis.
Memory links to those sources instead of copying them.

## Write rules

- Update memory only when a verified fact, durable decision, or recurring
  lesson changed.
- Include evidence (file, command, check, or authoritative URL) and remove stale
  entries in the same change.
- One parallel agent writes one `handoffs/YYYY-MM-DD-<task>-<agent>.md` file;
  never share an in-progress handoff file.
- A completed task folds durable information into `decisions.md`/`lessons.md`
  and deletes its obsolete handoff.
- Keep each entry short. If a topic needs a guide, put it in `docs/` or
  `openspec/` and link it.

See the `self-reflection` skill for when a surprise is worth recording here.
