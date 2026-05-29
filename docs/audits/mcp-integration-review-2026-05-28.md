# MCP Integration Review and Deep-Dive (2026-05-28)

## Scope

This review covers:

- Current MCP setup in `ekko`
- Comparison against `koda_automation` as baseline
- Documentation-backed recommendations for `shadcn`, `context7`, `gitnexus`
- Concrete implementation changes applied in this repository

## Executive Summary

The repository already had core MCP servers (`context7`, `shadcn`, `gitnexus`)
configured for VS Code and partially for Claude. The main gaps were governance
consistency and duplication risk:

1. Root `.mcp.json` existed alongside `.vscode/mcp.json`
2. No dedicated `.claude/mcp.json`
3. VS Code MCP discovery/autostart policy not explicitly enforced
4. Agent tool frontmatter did not consistently expose `gitnexus/*`
5. Documentation did not clearly define MCP source-of-truth and parity rules

All five gaps are now addressed.

## Evidence and Comparison (ekko vs koda_automation)

### What matched already

- `.vscode/mcp.json` present
- `context7`, `gitnexus`, `shadcn` configured
- Strong agent/skills/instructions structure in `.github/`

### What differed from baseline

- `koda_automation` uses `.claude/mcp.json` and avoids root `.mcp.json`
- `koda_automation` enforces MCP policy in docs (`AGENTS.md`, `copilot-instructions.md`)
- `koda_automation` aligns agent tool declarations with MCP families

### Why this mattered

Using both root `.mcp.json` and `.vscode/mcp.json` can introduce duplicate or
drifted entries. VS Code docs recommend explicit workspace config and careful
trust/lifecycle management for local MCP servers.

## Web and Documentation Research Notes

### shadcn MCP docs

Source: `https://ui.shadcn.com/docs/mcp`

Key points used:

- VS Code integration via `.vscode/mcp.json`
- Claude integration via `.mcp.json` (general guidance) but can be adapted to
  client-specific config files
- `components.json` registry support and namespace model
- Private registry authentication via environment variables
- Troubleshooting guidance for no-tools / registry access / install failures

### VS Code MCP docs

Sources:

- `https://code.visualstudio.com/docs/copilot/chat/mcp-servers`
- `https://code.visualstudio.com/docs/copilot/reference/mcp-configuration`

Key points used:

- Workspace MCP config should be in `.vscode/mcp.json`
- `chat.mcp.discovery.enabled` controls auto-discovery and can prevent duplicates
- `chat.mcp.autoStart` enables automatic restart/discovery after config changes
- Avoid hardcoding secrets; use input variables or env-file approaches

### Context7 docs

Sources:

- `https://github.com/upstash/context7`
- `https://context7.com/docs/resources/all-clients`
- `https://context7.com/docs/resources/troubleshooting`

Key points used:

- Remote HTTP endpoint `https://mcp.context7.com/mcp` is recommended and avoids
  local runtime friction
- API key can be supplied by header (`CONTEXT7_API_KEY`) when needed
- Troubleshooting confirms Windows-specific reliability considerations and remote endpoint benefits

### MCP core docs

Source: `https://modelcontextprotocol.io/`

Key points used:

- MCP is transport-agnostic (stdio / HTTP/SSE)
- Client/server trust and capability separation are core integration concerns

### GitNexus public docs availability

Attempts to fetch public package/repo pages for GitNexus from this environment
returned access errors for some endpoints. The implementation therefore uses:

- Existing in-repo GitNexus skill guidance
- Existing functional MCP configuration patterns already used in this repository and baseline repo

## Changes Implemented

### Configuration

- Added: `.claude/mcp.json`
  - `context7` (HTTP)
  - `shadcn` (stdio via `npx`, `frontend` cwd)
  - `gitnexus` (stdio via `bunx`, workspace cwd)

- Removed: root `.mcp.json`
  - Prevents duplicate discovery/drift with VS Code workspace MCP config

- Updated: `.vscode/settings.json`
  - `"chat.mcp.discovery.enabled": false`
  - `"chat.mcp.autoStart": true`

### Agent parity

Updated all `.github/agents/*.agent.md` frontmatter to include `gitnexus/*`.

Frontend agent now includes all three relevant tool families:

- `context7/*`
- `gitnexus/*`
- `shadcn/*`

### Documentation sync

Updated:

- `AGENTS.md`
- `.github/copilot-instructions.md`
- `CLAUDE.md`
- `.github/skills/gitnexus/SKILL.md`

to reflect the new MCP baseline and source-of-truth policy.

## Operational Guidance

### Recommended workflow

1. Keep VS Code MCP config in `.vscode/mcp.json`
2. Keep Claude Code MCP config in `.claude/mcp.json`
3. Do not reintroduce root `.mcp.json`
4. Keep `chat.mcp.discovery.enabled = false` to avoid duplicate entries
5. Keep `chat.mcp.autoStart = true` for smoother server lifecycle

### shadcn registry security

For private registries, define auth placeholders in
`frontend/components.json` and store real tokens in local environment files
(never committed).

### context7 auth and reliability

For most setups, remote HTTP mode is sufficient without local package runtime.
Add `CONTEXT7_API_KEY` only when rate limits/auth demands it.

## Follow-up Recommendations (Optional)

1. Add a small validation script/task that checks MCP policy invariants:
   - `.vscode/mcp.json` exists
   - `.claude/mcp.json` exists
   - root `.mcp.json` does not exist
2. Add a short onboarding section in `README.md` with MCP trust/start steps
  for new contributors.
3. Add an example `frontend/.env.local.example` for private shadcn registry
  auth variables if private registries are planned.

## Risk Assessment

- **Low risk**: Changes are config/docs/frontmatter only.
- **Primary impact**: Agent/tool discoverability and MCP lifecycle behavior.
- **Rollback**: Restore deleted root `.mcp.json` and revert doc updates if
  needed (not recommended due duplicate-risk).
