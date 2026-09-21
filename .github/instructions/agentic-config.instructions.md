---
description: Governance for editing this repo's multi-runtime agent configuration — skills, instructions/rules, agents, prompt/command façades, hooks, and the AGENTS.md/CLAUDE.md policy files. Keeps the .github/.claude/.agents trees portable and in parity.
applyTo: ".github/skills/**, .claude/skills/**, .agents/skills/**, .github/instructions/**, .claude/rules/**, .github/agents/**, .claude/agents/**, .github/prompts/**, .claude/commands/**, .github/hooks/**, .agents/agentic-setup/**, AGENTS.md, CLAUDE.md, .github/copilot-instructions.md"
---

# Agentic configuration governance

You are editing files that configure how every agent runtime behaves. Use the
`agent-config` and `create-skill` skills for the full procedure; the rules
below always apply.

## Placement — pick the right home

| You have… | Put it in… |
| --- | --- |
| An always-on constraint for files matching a glob | A paired instruction + rule (`.github/instructions/` ↔ `.claude/rules/`) |
| A reusable multi-step procedure | A skill (`<tree>/skills/<name>/SKILL.md`) |
| A cross-cutting, always-true policy | `AGENTS.md` (mirror the intent in `CLAUDE.md` and `copilot-instructions.md`) |
| A verified repo fact, decision, lesson, or handoff | `memories/` |

Prefer editing an existing file over adding one. Do not add a skill for what a
single instruction line covers, nor an instruction for a one-off.

## Three-tree parity (enforced by convention, verify manually)

- Skills are byte-identical across `.github/skills`, `.claude/skills`, and
  `.agents/skills` (`.agents/` is canonical). Create or edit all three together.
- Every instruction pairs with a rule of the same base name: an identical
  Markdown body, and scope globs that resolve to the same set (`applyTo` string ↔
  `paths` list).
- Agents pair across `.github/agents/<id>.agent.md` and `.claude/agents/<id>.md`
  where a Claude-side equivalent exists; the two rosters intentionally differ
  in a few platform-specific entries — see `CLAUDE.md`'s agent tables.
- Hooks mirror across `.github/hooks/*.json` and the `hooks` block in
  `.claude/settings.json`. MCP server names stay identical across
  `.claude/mcp.json` and `.vscode/mcp.json`. Change each pair together.

## Frontmatter

- An instruction file needs `description` + `applyTo`; a rule file needs
  `description` (optional) + `paths`. A skill needs `name` + `description` in
  its `SKILL.md` frontmatter.
- Keep `description` a one-sentence trigger: what it covers and when to use it.

## Before finishing

- Diff the documented tree in `CLAUDE.md` (§ agent-config directory listings)
  against the real directory contents — they drift silently; fix both in the
  same change.
- Re-read `AGENTS.md`/`CLAUDE.md`/`copilot-instructions.md` after any edit to
  confirm no policy got duplicated instead of linked.
