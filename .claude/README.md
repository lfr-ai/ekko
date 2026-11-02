# Claude Code configuration

Claude Code imports the shared operating policy from root `CLAUDE.md`, which in
turn imports `AGENTS.md`. Keep project-specific facts in `PROJECT.md`.

- Agents: `agents/`; implementation/review workers are under `agents/subagents/`.
- Rules: `rules/`, paired with `.github/instructions/`.
- Skills: `skills/`, byte-identical to `.agents/skills/` and `.github/skills/`.
- Commands: `commands/`, mirroring prompt files and command-backed skills.
- MCP: root `.mcp.json`; mirrored in `.vscode/mcp.json` and `.claude/mcp.json`.
- Settings and hooks: `settings.json`, using shared TypeScript hooks under
  `.agents/guard/`.

Run the parity and policy check with `task tools:agent-config:validate` or
`uv run --project backend python .agents/guard/verify_agent_config.py`.
