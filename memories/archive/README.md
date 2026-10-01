# Memory archive

Overflow for `memories/lessons.md` / `memories/decisions.md` once either
exceeds its guard-enforced line budget (`_MEMORY_LOG_LINE_BUDGET` in
`.agents/guard/verify_agent_config.py`). Not part of the routine read order in
[`memories/README.md`](../README.md) — consult only when investigating the
full incremental history behind a compressed entry in the live file.

## Rules

- Entries move here **verbatim**, unmodified, for provenance — never edited
  once archived.
- The live file keeps a short pointer back here (e.g. "full history in
  `archive/decisions.md`") so the compression is discoverable, not silent.
- Never restore an archived entry wholesale; if it becomes relevant again,
  write a fresh, current entry in the live file and link back here instead.
- This directory is exempt from the 400/500-line budget — it is meant to grow.
