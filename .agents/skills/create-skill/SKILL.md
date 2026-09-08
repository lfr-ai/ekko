---
name: create-skill
description: Author a new agent skill for this repository, or decide whether one is warranted. Use when a repeatable, multi-step, or project-specific workflow should be captured as a reusable SKILL.md across the three skill roots.
---

# Create a skill

## When to create one

Create a skill when a task is repeatable and non-trivial:

- The same multi-step workflow has come up roughly three or more times.
- It has project-specific steps, IDs, or gotchas worth capturing once.
- It needs consistent guardrails (secrets, destructive ops, required tooling).

Do not create a skill for a one-off, or for something a single instruction line
already covers.

## Create one proactively when

Without waiting to be asked, propose — and, once confirmed, author — a skill the
moment any of these is true:

- You have explained or reconstructed the same multi-step procedure a third time.
- You just recovered from a non-obvious gotcha that will recur; capture the fix.
- A workflow needs bundled guardrails (secrets, destructive commands, a required
  tool order) that a one-line rule cannot convey.
- A new subsystem lands that others will operate and whose steps are not obvious
  from the code.

If the trigger is a repo-specific *fact* rather than a *procedure*, prefer a
`/memories/repo/` note or an instruction line instead.

## Where it goes

Skills are mirrored across the three roots — create the same `SKILL.md` in each:
`.github/skills/`, `.claude/skills/`, `.agents/skills/`.

- Generic, reusable skills go at the root: `<root>/skills/<name>/SKILL.md`.
- Project-specific skills (they name this project, its hosts, or its IDs) go under
  the `project/` subfolder: `<root>/skills/project/<name>/SKILL.md`.

## Format

Each `SKILL.md` starts with YAML frontmatter, then a concise playbook body:

- `name`: kebab-case, matches the folder name.
- `description`: one line — what it does and when to use it, with concrete trigger
  phrases (the model reads this to decide when to invoke the skill).
- Keep path scopes out of skills; use paired `.github/instructions` and
  `.claude/rules` files. Prefer standard Agent Skills metadata; use a runtime
  extension only when every intended consumer supports it.
- Body: scannable steps, commands, guardrails, and references. The Documentation
  Style rule applies — minimal, no filler.
- Add `disable-model-invocation: true` only for manual-only skills.

## Consistency rubric

Match depth to the task, not a fixed length — but keep these consistent so skills
read like one library:

- **Every skill:** frontmatter (`name` + trigger-rich `description`), then a
  scannable body. Documentation Style applies: terse bullets/tables, no filler,
  no restated context. Respect cognitive load — a reader holds ~4 chunks, so use
  short named sections over long prose.
- **Convention skills** (e.g. `python-conventions`, `css-conventions`): state each
  rule, then a **good/bad example pair** and an **anti-patterns** list; link the
  paired instruction/rule instead of restating what it already enforces.
- **Workflow skills** (e.g. `opsx/*`, `database-migrations`): numbered steps,
  explicit guardrails (secrets, destructive ops, required order), and a final
  verification step.
- **Tool skills** (e.g. `gitnexus/*`, `jscpd`): commands, flags, and a clear
  "when to use / when not" note.

Trim, don't pad: if a skill grows past what a reader needs, split or shorten it
rather than adding sections for symmetry.

## After creating

- Top-level skills auto-load. A brand-new nested collection folder (such as
  `project/`) must be added to `chat.agentSkillsLocations` in `.vscode/settings.json`.
- Run the agent-config guard; it validates metadata, mirrored content, scopes,
  agents, hooks, portability, and MCP names.
