---
name: agent-config
description: Governance for this repo's multi-runtime agent setup — when to create a skill vs instruction/rule vs memory, and how to keep the .github/.claude/.agents trees portable and consistent. Use when adding or editing agent skills, instructions, rules, memories, or the AGENTS.md/CLAUDE.md policy.
---

# Agent configuration governance

This repo mirrors agent config across three runtime trees — `.github/` (Copilot),
`.claude/` (Claude Code) and `.agents/` (portable Agent Skills standard) — plus the
root `AGENTS.md` / `CLAUDE.md` policy. Keep all copies portable and consistent.

## Where does new guidance belong?

| You have… | Put it in… |
| --- | --- |
| An always-on constraint for files matching a glob | An **instruction/rule** (`.github/instructions/*.instructions.md` + `.claude/rules/*.md`) with `applyTo` / `paths` |
| A reusable multi-step *procedure* ("how to do X") | A **skill** (`<tree>/skills/<name>/SKILL.md`) |
| A cross-cutting, always-true policy | `AGENTS.md` (mirror the intent in `CLAUDE.md` and `copilot-instructions.md`) |
| An observed, repo-specific fact or lesson | **Memory** (`/memories/repo/`), not a committed file |

Create a **skill** once you have explained the same procedure twice, or the task
needs bundled scripts/references. Prefer editing an existing file over adding one.

## Portable vs project-specific

- **Portable** (default) — no repo-identifying facts; lives at `skills/<name>/`.
- **Project-specific** — lives at `skills/project/<name>/`, never referenced by a
  portable file.
- All project facts (package name, env-var prefix, paths, CI IDs, toolchain) live
  in **`PROJECT.md`** only. Portable guidance uses generic placeholders
  (`myapp`, `MYAPP_*`) and defers specifics to `PROJECT.md`.
- Instructions and rules stay portable — they defer project facts to `PROJECT.md`
  rather than growing a parallel `project/` tree. The only project-scoped things
  are `skills/project/` and `PROJECT.md`.
- `.agents/agentic-setup/` is the hidden machine-facing selection layer:
  `profiles.json` (capabilities per shape), `mcp-catalog.json` (opt-in MCP
  servers), `assets.json` with `assets/` (copyable agent-facing bundles), and
  `PROJECT.template.md`. It categorizes capabilities by project shape without
  moving standard discovery locations or creating a second human documentation
  tree.

## Canonical vs mirrored

`.agents/` is the portable, provider-neutral agent root — **not a third mirror**.
Per the Agent Skills standard, `.agents/skills/` is a default *cross-tool* location
(VS Code, Copilot CLI, and the Copilot cloud agent all read it), alongside the
provider-specific `.github/skills/` (GitHub) and `.claude/skills/` (Claude). Not
everything under `.agents/` is mirrored:

- **Mirrored to the provider trees** — anything a provider *auto-discovers* from
  its own location: skills (`.github/skills` ↔ `.claude/skills` ↔ `.agents/skills`,
  byte-identical), agents (`.github/agents` ↔ `.claude/agents`), instructions ↔
  rules, hooks, prompts ↔ commands, and MCP names. The guard enforces this parity.
- **Canonical-only (single source, never mirrored)** — content no provider
  auto-scans, read on demand: `.agents/agentic-setup/` (the selection layer) and
  `.agents/knowledge-base/` (repo-specific codebase knowledge). Mirroring
  repo-specific content across provider trees would be pointless triplication, so
  it lives once and is reached through the `AGENTS.md` → `PROJECT.md` →
  `.agents/knowledge-base/` pointer chain that every provider follows.

## Skill namespacing (subfolders)

Group skills under a subfolder **only** when they are sub-commands or steps of one
tool or workflow that has a dedicated prompt layer — the pattern used by
`gitnexus/` and `opsx/` (each has `.github/prompts/<name>/`). Discovery is not
recursive: every nested folder is registered explicitly in
`chat.agentSkillsLocations`, and a skill `name` must equal its leaf directory.

Keep these **flat** at the tree root:

- **Independent concern skills** (`frontend-*`, `accessibility`, `shadcn-ui`,
  `playwright`, `ui-ux-frontend`). Nesting would force leaf names
  (`configuration`, `structure`, `testing`, `debugging`) that collide with
  unrelated skills and lose the self-documenting prefix.
- **Vendored, name-invoked plugins** (`ponytail-*`). The skill name *is* the
  command (`/ponytail-audit`) and there is no prompt layer, so nesting would
  break invocation and diverge from upstream.

## Consistency (enforced)

- A skill must exist in **all three** trees at the same relative path with
  identical content.
- Apply convention edits to every copy
  (`.github/instructions` ↔ `.claude/rules` ↔ `.agents/skills`); `AGENTS.md` is
  the canonical wording when copies disagree.
- `scripts/agents/verify_agent_config.py` (pre-commit `agent-config-guard`) checks
  skill metadata/parity, portable-token leakage, agent rosters, instruction/rule
  scopes, hook parity and MCP parity — run it after any change.
- Runtime hooks are mirrored across runtimes: `.github/hooks/*.json` and the
  `hooks` block in `.claude/settings.json` wire the same `hooks/scripts/*`
  behavior. Change both together.

## Reusing this setup elsewhere

Use `project-bootstrap`: copy the trees, delete every `**/skills/project/`
folder, rewrite `PROJECT.md` (including explicit agent-portability tokens), and
remove shape-specific agents/MCP servers that the new project does not use.
Everything else is project-agnostic.

## Documentation style

README, `docs/` and CHANGELOG stay minimal and scannable — terse bullets, small
tables, no AI boilerplate or restated context. A short doc that gets read beats a
complete one that does not.
