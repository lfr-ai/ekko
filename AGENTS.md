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

## OpenSpec baseline

Use OpenSpec for non-trivial work. Recommended path:

1. propose
2. apply
3. sync
4. verify
5. archive

Use behavior-first deltas (ADDED/MODIFIED/REMOVED).
