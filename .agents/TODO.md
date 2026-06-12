# Agentic Topology TODO

Governance checklist for parity, tooling policy, MCP consistency, and
production-readiness criteria.

## Parity Enforcement

- [x] Skills parity across `.github/skills`, `.claude/skills`, `.agents/skills`
- [x] OpenSpec prompts synced to grouped `openspec/` subfolders
- [x] OpenSpec commands synced to grouped `openspec/` subfolders
- [x] GitNexus prompts and commands scaffolded in all surfaces
- [x] Agent profiles synced from `.claude/agents` to `.agents/agents`
- [x] `sync_agentic_setup.py` created and operational (0 drift on last run)

## Tooling Policy

- [x] `ruff` is the only linter/formatter
- [x] `ty` is the only type checker
- [x] `pyright` removed from all configurations and plugins
- [x] `ms-pyright.pyright` added to `unwantedRecommendations` in extensions.json
- [x] `astral-sh.ty` added to VS Code extension recommendations
- [x] Verify no `pyright` references remain in any config file
- [x] `pre-commit` hooks aligned with koda_automation baseline

## MCP Consistency

- [x] `.vscode/mcp.json` defines authoritative workspace MCP servers
- [x] `.agents/mcp.servers.json` mirrors neutral baseline
- [x] `context7`, `gitnexus`, `playwright` present in all MCP configs
- [x] `shadcn` present (ekko-specific, frontend stack)

## Production Readiness

- [x] Clean Architecture boundaries enforced via pre-commit hook
- [x] Magic string checker operational
- [x] Module docstring checker operational
- [x] Architecture boundary checker operational
- [x] Dependency audit hook configured
- [x] jscpd copy-paste detection in pre-commit (single hook, no duplicates)
- [x] lychee link checking in pre-commit
- [x] xenon complexity gate configured
- [x] bandit security scanning configured
- [x] detect-secrets baseline maintained
- [x] Dependencies resolved with no conflicts (crewai + otel pinned)
- [x] Dev dependency versions aligned with koda_automation baseline

## Skills Alignment with koda_automation

- [x] `clean-architecture/SKILL.md`
- [x] `ddd/SKILL.md`
- [x] `dry-refactoring/SKILL.md`
- [x] `gitnexus/SKILL.md` (flat — ekko uses single SKILL.md)
- [x] `jscpd/SKILL.md`
- [x] `openspec/SKILL.md` (plus individual subskills)
- [x] `python-conventions/SKILL.md`
- [x] `quality-gate/SKILL.md`
- [x] `sdd/SKILL.md`
- [x] `tdd/SKILL.md`
- [x] `testing-conventions/SKILL.md`

## Ekko-specific Additions (beyond koda baseline)

- [x] `frontend-react-stack/SKILL.md`
- [x] `naming-registry/SKILL.md`
- [x] `deploy-check/SKILL.md`
- [x] Frontend agents: `frontend-react.agent.md`, `frontend-reviewer.md`
- [x] Database agent: `database.agent.md`
- [x] Security agent: `security.agent.md`

## Validation Commands

Run these after any agentic/config change:

1. `uv run --project backend python .agents/sync_agentic_setup.py`
2. `uv run --project backend ruff check .agents/sync_agentic_setup.py`
3. `uv run --project backend pre-commit validate-config`
4. `uv lock` (in backend/)

## Exit Criteria (all met)

- [x] No references to pyright remain in project-controlled agentic config
- [x] Ty and Ruff are the only documented lint/type-check defaults
- [x] Grouped prompt/command structure is consistent across surfaces
- [x] MCP server set is consistent across VS Code, Claude, and neutral topology
- [x] Sync script can be run repeatedly with no unintended diffs
- [x] Dependency resolution clean (no conflicts)
