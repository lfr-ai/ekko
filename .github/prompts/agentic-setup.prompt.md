---
description: "Bootstrap the portable agentic setup for a NEW project, or onboard/refresh it for an EXISTING one. Orchestrates the project-bootstrap and codebase-onboarding skills, then verifies with the agent-config guard."
agent: agent
---

Bootstrap or refresh the portable agentic setup for this repository.

Decide the mode from the repository state, then follow the matching path. This
prompt **orchestrates existing skills** — it does not restate their steps. Treat
`project-bootstrap`, `codebase-onboarding`, `agent-config`, `create-skill`, and
`consistency` as the source of truth.

## Choose the mode

- **New project** — no `.agents/agentic-setup/`, or an empty repo you are standing
  up: scaffold the setup from scratch (Path A).
- **Existing project** — code exists and you are adding or refreshing the agentic
  setup, knowledge base, specs, memory, and index (Path B).

If unsure, inspect `AGENTS.md`, `.agents/agentic-setup/profiles.json`, `PROJECT.md`,
`.agents/knowledge-base/`, `openspec/`, and the GitNexus index, then choose.

## Constraints (non-negotiable)

- Canonical policy is `AGENTS.md`. Keep `CLAUDE.md` (`@AGENTS.md`) and
  `.github/copilot-instructions.md` as **thin layers** — never re-duplicate policy.
- Project facts live only in `PROJECT.md`; portable skills use generic placeholders.
- **uv + Task** (Python) / **Bun** (frontend) only. No `git` commands. No secrets.
- Skills stay mirrored byte-identically across `.github/skills`, `.claude/skills`,
  `.agents/skills`; each instruction pairs with a `.claude/rules` file of equal scope.

## Path A — New project

1. Run `project-bootstrap`: choose the shape (backend / frontend / full-stack),
   resolve the `extends` chain in `.agents/agentic-setup/profiles.json`, and copy
   only the selected capabilities. Rewrite `PROJECT.md` from
   `.agents/agentic-setup/PROJECT.template.md`, including agent-portability tokens.
2. Delete every `**/skills/project/` folder copied from the source; remove
   shape-specific agents and MCP servers the project will not use.
3. Wire MCP (`.mcp.json`, `.vscode/mcp.json`), hooks, and the discovery locations
   in `.vscode/settings.json` for any new nested skill/prompt folders.
4. Run the agent-config guard, then scaffold application layers per the shape's
   structure skills.

## Path B — Existing project (onboard / refresh)

1. Run `codebase-onboarding`: discover shape, layers, entry points, tests, config,
   and specs from files and code intelligence before writing anything.
2. Refresh `PROJECT.md` — identity, toolchain, architecture layers, ubiquitous
   language, spec/data locations, CI/deploy, code-intelligence commands, tokens.
3. Populate/refresh the agent knowledge base at `.agents/knowledge-base/` (README
   index, `architecture`, `domain-glossary`, `flows`, `design-decisions`).
   **Synthesize and index** the authoritative sources — never duplicate
   `PROJECT.md` or specs.
4. Initialize or update OpenSpec (`openspec/specs/`) from **verified** behavior
   only; preserve significant design decisions in change/archive artifacts.
5. Refresh the GitNexus index (`task graph`) after new/renamed/moved modules;
   record verified gotchas and commands under `/memories/repo/`.
6. Confirm every convention is covered by an instruction/rule + skill; add any
   missing one with `create-skill` (follow its consistency rubric) and pair scopes.

## Verify (both paths)

- `uv run python scripts/agents/verify_agent_config.py` passes (skill/agent parity,
  portability, instruction↔rule scopes, hooks, MCP names, profiles/catalogs).
- `openspec validate --all` passes when specs exist.
- A fresh agent can locate entry points, layers, tests, config, and the validation
  gate from `PROJECT.md` + `.agents/knowledge-base/` alone.
- No project tokens leaked into portable skills; no secrets committed; no `git` run.

End with a short `tldr;` listing the mode chosen, artifacts created/refreshed, and
the guard result.
