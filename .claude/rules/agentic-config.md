---
paths:
  - ".github/skills/**"
  - ".claude/skills/**"
  - ".agents/skills/**"
  - ".github/instructions/**"
  - ".claude/rules/**"
  - ".github/agents/**"
  - ".claude/agents/**"
  - ".github/prompts/**"
  - ".claude/commands/**"
  - ".github/hooks/**"
  - ".claude/settings.json"
  - ".vscode/settings.json"
  - ".mcp.json"
  - ".vscode/mcp.json"
  - ".claude/mcp.json"
  - ".warp/.mcp.json"
  - ".agents/agentic-setup/**"
  - ".agents/guard/**"
  - "AGENTS.md"
  - "CLAUDE.md"
  - "PROJECT.md"
  - ".github/copilot-instructions.md"
  - "llms.txt"
---

# Agentic configuration governance

You are editing files that configure how every agent runtime behaves. Use the
`agent-config` and `create-skill` skills for the full procedure; the rules below
always apply and are verified by `.agents/guard/verify_agent_config.py`.

## Placement — pick the right home

| You have… | Put it in… |
| --- | --- |
| An always-on constraint for files matching a glob | A paired instruction + rule (`.github/instructions/` ↔ `.claude/rules/`) |
| A reusable multi-step procedure | A skill (`<tree>/skills/<name>/SKILL.md`) |
| A cross-cutting, always-true policy | `AGENTS.md` (mirror the intent in `CLAUDE.md` and `copilot-instructions.md`) |
| A verified repo fact, decision, lesson, or handoff | `memories/` |

## Refactor first — extend and link, don't restate

Before adding any file, or a new section to an existing one, anywhere in this
tree (or in `AGENTS.md`, `PROJECT.md`, `llms.txt`, or `memories/`):

1. Text-search all three trees plus `memories/` for existing coverage — not just
   the file you are about to touch.
2. Found it? Extend that file, or add a cross-link (a relative Markdown path);
   never write a second description of the same rule. One concept keeps one home
   and every other mention links to it.
3. Editing a `memories/` log at or near its budget? Consolidate or archive first
   (see the `self-reflection` skill), never raise the budget.
4. Only when the search finds nothing does a new file get created, per the table
   above. Do not add a skill for what one instruction line covers, nor an
   instruction for a one-off.

The `agent-config` skill's refactor-first checklist is the long form; this is the
always-on trigger.

## Three-tree parity (enforced)

- Skills are byte-identical across `.github/skills`, `.claude/skills`, and
  `.agents/skills` (`.agents/` is canonical). Create or edit all three together;
  `uv run .agents/skills/agent-config/scripts/sync.py --apply` copies canonical
  skills into the mirrors.
- Every instruction pairs with a rule of the same base name: an identical
  Markdown body, and scope globs that resolve to the same set (`applyTo` string ↔
  `paths` list). Register the pair in the guard's `_INSTRUCTION_RULE_PAIRS`.
- Agents pair across `.github/agents/<id>.agent.md` and `.claude/agents/<id>.md`
  with an identical body; the Claude copy always sets `user-invocable: false`.
- Directly invoked skill families expose thin `.github/prompts/<family>/` and
  `.claude/commands/<family>/` façades; hooks mirror across `.github/hooks/*.json`
  and the `hooks` block in `.claude/settings.json`. MCP server names stay
  identical across `.mcp.json`, `.vscode/mcp.json`, and `.claude/mcp.json`. Change
  each pair together.
- Discovery and index surfaces are governed too: `llms.txt` is the agent entry
  index (keep every link valid and pointed at a real file); `.vscode/settings.json`
  decides what loads (`chat.useAgentsMdFile`, hook sources, MCP startup) and must
  not reintroduce deprecated `chat.*Locations` settings; `PROJECT.md` holds the
  project facts every portable file defers to. The guard checks these — edit them
  deliberately, not incidentally.

## Frontmatter

- Skill: `name` (kebab-case, matches its directory, globally unique) plus a
  trigger-rich `description`. Use only portable Agent Skills fields; never put an
  `applyTo`/`paths` scope in a skill.
- Instruction: `description` + `applyTo` (one comma-joined glob string). Rule:
  `paths` (a YAML list). Keep the two bodies identical.

## Budgets and portability

- Keep each instruction/rule at or under 140 lines and each `SKILL.md` under 500.
  Never raise a frozen line budget to fit content — trim, or move worked examples
  into the matching skill.
- Portable files carry no project identity (use `myapp`/`MYAPP_*` placeholders and
  defer facts to `PROJECT.md`); project-specific skills live under
  `skills/project/`.
- Add every new skill, agent, or instruction to
  `.agents/agentic-setup/profiles.json` under the right shape, or the guard
  reports an uncategorized capability.

## Before finishing

Run `uv run python .agents/guard/verify_agent_config.py`. When a governance
change reflects a real decision, record its *why* in `memories/decisions.md` so
the next agent does not re-litigate it.
