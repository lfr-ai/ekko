# Claude Code

@AGENTS.md

This file contains only Claude Code CLI-specific guidance. Shared policy lives in
`AGENTS.md`; project facts and commands live in `PROJECT.md`.

## Claude-specific configuration

- MCP servers: root `.mcp.json` (kept in parity with `.vscode/mcp.json` and
  `.claude/mcp.json`).
- Settings and hooks: `.claude/settings.json`.
- Agents: `.claude/agents/` (primary agents at the root; bounded workers under
  `subagents/`).
- Rules and skills: `.claude/rules/` and `.claude/skills/`.
- Commands: `.claude/commands/`.

Claude Code reads `CLAUDE.md` and imports `AGENTS.md` above. Do not duplicate the
shared rules here. Validate shared agent configuration with
`uv run python .agents/guard/verify_agent_config.py`.

### Agent profiles

| Agent | Claude definition |
| --- | --- |
| backend-implementer | `.claude/agents/subagents/backend-implementer.md` |
| code-reviewer | `.claude/agents/subagents/code-reviewer.md` |
| codebase-researcher | `.claude/agents/subagents/codebase-researcher.md` |
| contract-iac-lint | `.claude/agents/subagents/contract-iac-lint.md` |
| ddd | `.claude/agents/ddd.md` |
| debug | `.claude/agents/debug.md` |
| deep-thinking | `.claude/agents/deep-thinking.md` |
| devops | `.claude/agents/devops.md` |
| devops-implementer | `.claude/agents/subagents/devops-implementer.md` |
| docs-writer | `.claude/agents/subagents/docs-writer.md` |
| frontend | `.claude/agents/frontend.md` |
| frontend-implementer | `.claude/agents/subagents/frontend-implementer.md` |
| fullstack | `.claude/agents/fullstack.md` |
| modernization | `.claude/agents/modernization.md` |
| orchestrator | `.claude/agents/orchestrator.md` |
| plan-architect | `.claude/agents/subagents/plan-architect.md` |
| planner | `.claude/agents/subagents/planner.md` |
| refactor | `.claude/agents/refactor.md` |
| sdd | `.claude/agents/sdd.md` |
| security-reviewer | `.claude/agents/subagents/security-reviewer.md` |
| solid-review | `.claude/agents/subagents/solid-review.md` |
| tdd | `.claude/agents/tdd.md` |
| test-author | `.claude/agents/subagents/test-author.md` |
| testing | `.claude/agents/testing.md` |

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **ekko** (4319 symbols, 6489 relationships, 85 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/ekko/context` | Codebase overview, check index freshness |
| `gitnexus://repo/ekko/clusters` | All functional areas |
| `gitnexus://repo/ekko/processes` | All execution flows |
| `gitnexus://repo/ekko/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
