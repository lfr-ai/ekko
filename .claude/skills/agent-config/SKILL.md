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
| A verified repo-specific fact, decision, lesson, or handoff | Root **`memories/`** |

Create a **skill** once you have explained the same procedure twice, or the task
needs bundled scripts/references. Prefer editing an existing file over adding one.

## Refactor-first checklist (before adding anything)

Before creating a new file, or appending a new section to an existing one,
anywhere in this tree (skill, instruction/rule, agent, or memory entry):

1. Search all three trees plus `memories/` for existing coverage of the topic
   (a text search across `.github/`, `.claude/`, `.agents/`, `memories/` — not
   just the tree you are about to edit).
2. Found existing coverage? Edit or extend it, add a cross-link, or fold a
   memory entry into it. Do not write a second description of the same rule.
3. Editing `memories/lessons.md`/`decisions.md` and the file is at or near its
   line budget? Consolidate first (merge a near-duplicate entry, archive a
   resolved one) — see `memories.instructions.md` and `self-reflection`.
4. Only once 1-2 turn up nothing does a new file get created, per the
   placement table above.
5. Run `verify_agent_config.py` before finishing — the one automated check
   for parity, budgets, and placement across the whole tree.

This is the concrete form of "prefer editing an existing file over adding
one" — re-read it before any agentic-setup change, not just when unsure
where something belongs.

## Agent visibility, subagents, and layout

Two independent frontmatter flags — they replace the deprecated `infer` —
control how each agent is reachable, verified against VS Code's
[custom-agents](https://code.visualstudio.com/docs/copilot/customization/custom-agents)
and [subagents](https://code.visualstudio.com/docs/agents/run/subagents) docs
(2026-09-28):

- **`user-invocable`** — dropdown visibility, in both Local and Copilot; `false`
  hides a subagent-only helper from the picker (it stays usable as a subagent).
- **`disable-model-invocation`** — whether *other* agents may invoke it as a
  subagent; `false` (default) = available as a worker, `true` = top-level only.

Both runtimes discover agent definitions **recursively** (subfolders are fine)
but resolve a subagent by its **kebab-case identifier** (its file basename), not
the Title-Case `name` display value — verified live 2026-09-28: a `runSubagent`
probe resolved `codebase-researcher` but not `Codebase Researcher`, and an
`agents` allowlist entry gates an invocation only when it is that identifier.
`name` therefore stays a Title-Case display label that normalizes to the
identifier, while every `agents` entry, `runSubagent` call, and body invocation
reference uses the kebab identifier (== filename; Claude Code likewise expects
lowercase-hyphen names). **Workers live in the `subagents/` subfolder** while
primary modes and the orchestrator stay flat; identifiers stay globally unique
across the whole tree.
Three tiers follow:

- **Primary modes** (`fullstack`, `ddd`, `sdd`, `tdd`, `debug`, `deep-thinking`,
  `devops`, `frontend`, `modernization`, `refactor`, `testing`) sit flat in
  `.github/agents/`. Each sets `disable-model-invocation: true`, keeps the
  `agent` tool, and lists only its relevant workers, by kebab identifier, in an
  explicit `agents` allowlist — never `['*']`. The `.github` copy explicitly sets
  `user-invocable: true`; the `.claude` copy sets it `false` so VS Code does not
  double-list the mirror (the flag is inert for Claude Code CLI).
- **`orchestrator`** — the master coordinator (flat, user-invocable), building on
  `deep-thinking` + `fullstack`. It sets `disable-model-invocation: true`
  (top-level only, never a worker), the `agent` tool, an explicit allowlist of
  every worker, and a strong `model`. Follow Planner → Plan Architect → one
  bounded Implementer → relevant Reviewer(s); do not clone `fullstack`.
- **Subagent-only workers** live under `<tree>/agents/subagents/` and are
  classified by the guard's explicit worker roster: planning (`planner`,
  `plan-architect`), discovery (`codebase-researcher`), bounded implementation
  (`backend-implementer`, `frontend-implementer`, `devops-implementer`,
  `test-author`, `docs-writer`), and review (`code-reviewer`, `solid-review`,
  `security-reviewer`, `contract-iac-lint`). Each sets
  `user-invocable: false`, `disable-model-invocation: false`, and `agents: []`
  in **both** trees. Research/review workers are read-only; only the bounded
  implementers get `edit`/`execute`, and none gets `agent`. Every worker pins a
  **small** model: a Haiku/mini priority list in `.github`, `haiku` in `.claude`.

Model precedence for a subagent: the `runSubagent` call's explicit model, then
the agent's `model`, then the main conversation's — and any explicit/configured
pick is capped at the main model's cost tier. The guard requires workers under
`subagents/` (primary modes stay flat) and enforces roster/name/body parity, the
125-line budget, both roster
tables, profile categorization, picker visibility, invocation flags, worker
models/tools, and coordinator allowlists. Also confirm live discovery in the
chat customization diagnostics view after adding or moving an agent.

## Portable vs project-specific

- **Portable** (default) — no repo-identifying facts; lives at `skills/<name>/`.
- **Project-specific** — lives at `skills/project/<name>/`, never referenced by a
  portable file.
- All project facts (package name, env-var prefix, paths, CI IDs, toolchain) live
  in **`PROJECT.md`** only. Portable guidance uses generic placeholders
  (`myapp`, `MYAPP_*`) and defers specifics to `PROJECT.md`.
- Instructions and rules stay portable — they defer project facts to `PROJECT.md`
  rather than growing a parallel `project/` tree. The only project-scoped
  locations are `PROJECT.md`, `**/skills/project/`, `.agents/knowledge-base/`
  (this codebase's synthesis), and `memories/` (this repo's working state); on
  reuse they are rewritten, dropped, or reinitialized. Everything else is portable.
- `.agents/agentic-setup/` is the hidden machine-facing selection layer:
  `profiles.json` (capabilities per shape, including active MCP servers),
  `assets.json` with `assets/` (copyable agent-facing bundles), and
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

## How each runtime discovers AGENTS.md / CLAUDE.md / copilot-instructions.md

Verified against each vendor's own docs (2026-09-08) — re-check if a vendor
changes this rather than trusting this note indefinitely:

- **VS Code Copilot Chat** auto-detects and *combines* all three into every
  chat request — `copilot-instructions.md` unconditionally, `AGENTS.md` when
  `chat.useAgentsMdFile: true`, `CLAUDE.md` when `chat.useClaudeMdFile: true`
  (this repo sets the latter `false` — see `.vscode/settings.json`).
  [Use custom instructions in VS Code](https://code.visualstudio.com/docs/copilot/customization/custom-instructions)
  — "VS Code combines and adds them to the chat context, no specific order
  is guaranteed."
- **GitHub Copilot** (github.com, cloud agent, code review) does the same:
  `copilot-instructions.md` (repository-wide) and `AGENTS.md` (agent
  instructions) are both provided when both exist.
  [Adding repository custom instructions for GitHub Copilot](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)
- **Claude Code (CLI)** does **not** auto-discover `AGENTS.md`: "Claude Code
  reads CLAUDE.md, not AGENTS.md." It only sees `AGENTS.md` through the
  explicit `@AGENTS.md` import at the top of `CLAUDE.md` (present in this
  repo) — Anthropic's own documented pattern for this exact situation.
  Anthropic also recommends under 200 lines of total loaded content per
  session (imports count, since "imported files still load ... at launch").
  [How Claude remembers your project](https://code.claude.com/docs/en/memory#agentsmd)
- **`AGENTS.md` itself** is a vendor-neutral format stewarded by the Agentic
  AI Foundation (Linux Foundation), used across 60k+ repos and many agents —
  why it stays the one canonical policy file instead of a vendor-specific one.
  [agents.md](https://agents.md/)

Net effect: no context is lost for either tool today. The one thing that
would silently drop the whole Hard Rules layer is `chat.useAgentsMdFile`
turning `false` in VS Code, or the `@AGENTS.md` import line disappearing
from `CLAUDE.md` — check both after any `.vscode/settings.json`/`CLAUDE.md`
edit. `.agents/guard/verify_agent_config.py` also enforces a line-count
budget on all three files (see `_POLICY_FILE_LINE_BUDGETS`) so none of them
can silently grow past what a session should load.

## Skill namespacing (subfolders)

- Keep a singleton skill flat at `<tree>/skills/<name>/SKILL.md`.
- Group a cohesive multi-skill family under `<tree>/skills/<family>/<leaf>/`.
  Current families are `frontend/`, `gitnexus/`, `opsx/`, `ponytail/`, and
  project-specific `project/`.
- A family root never contains its own `SKILL.md`; behavior lives in concise leaf
  skills only (for example `frontend/testing`, `ponytail/audit`).
- Discovery is native: current VS Code and Agent Host discover the standard
  customization trees without deprecated `chat.*Locations` settings.
- A skill `name` equals its leaf directory and must be globally unique across
  canonical `.agents/skills`, even when IDs have different family paths.
- Directly invoked nested families expose thin `.github/prompts/<family>/` and
  `.claude/commands/<family>/` façades that delegate to the mirrored skill body.
- Public command syntax follows each runtime's established family convention:
  Copilot uses an explicit hyphenated prompt name (`/frontend-testing`,
  `/ponytail-audit`, like `/opsx-apply`); Claude uses its directory-qualified
  command (`/frontend:testing`, `/ponytail:audit`, like `/opsx:apply`). Bare leaf
  names are internal skill identities, not the documented invocation surface.

## Consistency (enforced)

- A skill and all bundled resources must exist in **all three** trees at the same
  relative paths with identical content.
- Apply convention edits to every copy
  (`.github/instructions` ↔ `.claude/rules` ↔ `.agents/skills`); `AGENTS.md` is
  the canonical wording when copies disagree.
- `.agents/guard/verify_agent_config.py` (pre-commit `agent-config-guard`) checks
  skill metadata/parity, family layout, retired flat IDs, discovery roots,
  façade names/targets, portable-token leakage, agent rosters, instruction/rule
  scopes, hook parity and MCP parity — run it after any change.
- Runtime hooks are mirrored across runtimes: `.github/hooks/*.json` and the
  `hooks` block in `.claude/settings.json` wire the same Bun-run guard scripts
  in `.agents/guard/*.ts` (`tool-guardian`, `license-guardian`,
  `session-context`). Change both together. VS Code must load only
  `.github/hooks`; `.vscode/settings.json` disables its default discovery of
  `.claude/settings.json` so mirrored hooks do not execute twice. Every shared
  hook self-filters because VS Code currently ignores Claude matcher values.

Run `uv run .agents/skills/agent-config/scripts/sync.py` to check skill mirrors.
Use `--apply` only to copy canonical `.agents/skills` files into provider mirrors;
it never deletes extras, which remain an explicit human-reviewed cleanup.

## Reusing this setup elsewhere

Use `project-bootstrap`: copy the trees, remove every `**/skills/project/`
folder through reviewed workspace edits, rewrite `PROJECT.md` (including explicit
agent-portability tokens), initialize `memories/`, and remove shape-specific
agents/MCP servers the new project does not use. Everything else is
project-agnostic.

## Documentation style

README, `docs/` and CHANGELOG stay minimal and scannable — terse bullets, small
tables, no AI boilerplate or restated context. A short doc that gets read beats a
complete one that does not.
