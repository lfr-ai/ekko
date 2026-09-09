# Agentic setup

Machine-facing capability selection for Ekko's portable multi-runtime agent configuration.

## Files

- `profiles.json` categorizes the capabilities present in this full-stack repository.
- `mcp-catalog.json` lists opt-in MCP servers that require a local or external service.
- `assets.json` indexes reusable setup assets.
- `PROJECT.template.md` is the portable starting point for another repository's facts.
- `PROJECT.md` at the repository root is Ekko's factual overlay.

Skills remain byte-identical across `.github/skills`, `.claude/skills`, and
`.agents/skills`. Provider-specific agents and instruction/rule scopes may differ
where their runtimes or Ekko's monorepo structure require it.

Validate changes with
`uv run --project backend python tools/conventions/check_agent_customizations.py`.
