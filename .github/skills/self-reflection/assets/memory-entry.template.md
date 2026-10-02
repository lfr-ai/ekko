# Memory entry template

Copy this shape when adding a lesson or decision to `memories/lessons.md`,
`memories/decisions.md`, or a `/memories/repo/*.md` note. Keep it as tight as
the example — a paragraph of hedging is worse than a missing entry, because
no one will read past the first line.

```markdown
- **<short, specific title of the surprise or decision>**: <one sentence: what
  happened / what was decided>. <one sentence: the concrete evidence — file,
  command, log line, or authoritative source>. <optional one sentence: the
  fix or the rule going forward>.
```

## Worked example (a bug caused by a wrong assumption)

```markdown
- **`get_config()` returns `None` outside app context**: called it from a
  background job and hit `AttributeError: NoneType has no attribute env`.
  Confirmed via `grep -n "def get_config" src/**/*.py` — it reads
  `app.state.config`, which only exists inside a request. Fix: background
  jobs must receive `config` as an explicit argument, never call `get_config()`.
```

## Worked example (a governance/agentic-setup gap)

```markdown
- **`frontend` agent missing from Agent Profiles tables**: `.github/agents/
  frontend.agent.md` existed and `profiles.json` listed it, but `AGENTS.md`'s
  human-readable table never gained a row — no guard checks table
  completeness against the `agents/` directory. Fixed: added the row to all
  3 policy files. Lesson: spot-check `list_dir agents/` vs the table after
  adding any new agent file; nothing automates this.
```

## Fields that make an entry worth keeping

- **Specific enough to grep for** — a future agent should be able to search
  the exact symptom (error message, command, filename) and land on this entry.
- **Evidence, not narration** — cite the file/command/log that proves it, not
  a description of the investigation process.
- **Actionable** — end with the fix, the rule, or the decision; a lesson that
  only describes a problem without a resolution is half-written.
- **Deduplicated** — before writing, check the entry does not already exist
  in `AGENTS.md`, an instruction file, or another memory entry (see the
  Anti-patterns section in `SKILL.md`).

## After writing

If the surprise exposed a stale/missing skill, instruction, rule, or MCP
entry, fix that first (`agent-config` skill's placement rules), verify with
`.agents/guard/verify_agent_config.py`, and only then record the entry — the
fix and the reason travel together.
