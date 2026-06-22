# AGENTS.md

Platform-agnostic policy for coding agents.

## Hard rules

1. No `Any` in production typing.
2. Prefer immutable dataclasses for value-like types.
3. Remove dead code in the same change set.
4. Respect architecture boundaries (dependencies flow inward).
5. No legacy compatibility shims unless explicitly required.
6. No agent-run `git` shell commands.
7. Keep docs and config in sync with code changes.

## Agent profiles

| Agent | Use for |
| --- | --- |
| `frontend-react` | React/TypeScript architecture and component patterns |
| `ui-ux` | accessibility, UX consistency, interaction design |
| `storybook` | component stories, docs, visual interaction tests |
| `playwright` | end-to-end coverage, trace-first debugging |
| `shadcn` | shadcn/ui composition and CLI-driven component workflows |
| `testing` | test strategy, coverage, reliability |
| `security` | application security and dependency hardening |
| `devops` | containerization, CI/CD, deployment/IaC |
| `debug` | root-cause analysis and verification |
| `deep-thinking` | cross-cutting design tradeoffs and migration plans |
| `refactor` | behavior-preserving simplification |
| `modernization` | staged modernization and deprecation planning |
| `backend-python` | typed backend architecture and API service design |
| `database` | migration-safe schema and query design |
| `ddd` | domain modeling and bounded-context consistency |
| `sdd` | behavior-first executable specifications |
| `tdd` | Red-Green-Refactor implementation loops |

## MCP baseline

Keep these available and aligned across runtime configs:

- `context7`
- `gitnexus`
- `playwright`
- `shadcn` (frontend repositories)
- `storybook` (frontend component workflows)

## OpenSpec baseline

Use OpenSpec for non-trivial work. Recommended path:

1. propose
2. apply
3. sync
4. verify
5. archive

Use behavior-first deltas (ADDED/MODIFIED/REMOVED).

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **voice-bot** (4221 symbols, 6507 relationships, 65 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

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
| `gitnexus://repo/voice-bot/context` | Codebase overview, check index freshness |
| `gitnexus://repo/voice-bot/clusters` | All functional areas |
| `gitnexus://repo/voice-bot/processes` | All execution flows |
| `gitnexus://repo/voice-bot/process/{name}` | Step-by-step execution trace |

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
