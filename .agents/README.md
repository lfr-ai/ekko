# Neutral Agentic Topology (`.agents`)

This folder is the **neutral, cross-agent canonical topology** for this repository.

## Purpose

- Keep agentic assets organized independently of any single client.
- Mirror critical capabilities from `.github/` and `.claude/`.
- Provide a parity contract via `agentic-topology.json` and `parity-map.json`.

## Structure

- `skills/` — shared skill graph (including nested domains like `openspec/` and `gitnexus/`)
- `prompts/` — neutral prompts grouped by domain
- `commands/` — neutral commands grouped by domain
- `agents/` — neutral agent profiles
- `mcp.servers.json` — neutral MCP server baseline

## Synchronization

Run the sync utility after updating `.github` prompts/skills or `.claude` commands/agents:

- `scripts/sync_agentic_setup.py`

This script is idempotent and currently synchronizes:

1. `.github/skills/**/SKILL.md` -> `.agents/skills/**/SKILL.md`
2. `.github/prompts/opsx-*.prompt.md` ->
   - `.github/prompts/openspec/*.prompt.md`
   - `.agents/prompts/openspec/*.prompt.md`
3. `.claude/commands/opsx/*.md` ->
   - `.claude/commands/openspec/*.md`
   - `.agents/commands/openspec/*.md`
4. `.claude/agents/*.md` -> `.agents/agents/*.md`
5. Bootstrapped GitNexus prompt/command scaffolding in all relevant folders.

## Best-practice constraints

- Keep `.agents` tracked in git (do not ignore it).
- Keep domain organization consistent (`openspec`, `gitnexus`, etc.).
- Avoid cross-folder hidden coupling; use explicit parity mapping.
- Keep the three surfaces independently usable:
  - `.github/` for Copilot
  - `.claude/` for Claude Code
  - `.agents/` for neutral canonical topology
