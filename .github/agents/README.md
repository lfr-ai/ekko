# VS Code Copilot Agents

Custom agents for VS Code GitHub Copilot, stored as `.agent.md` files with YAML frontmatter.

## Available Agents

| Agent | File | Purpose |
|-------|------|---------|
| Backend Python | `backend-python.agent.md` | Clean Architecture, FastAPI, SQLAlchemy |
| Frontend React | `frontend-react.agent.md` | React 19, TypeScript, shadcn/ui, Tailwind v4 |
| Testing | `testing.agent.md` | pytest, Vitest, Playwright, Hypothesis |
| Database | `database.agent.md` | SQLAlchemy, Alembic, repository pattern |
| Security | `security.agent.md` | OWASP, auth, vulnerability prevention |
| Debug | `debug.agent.md` | Systematic bug investigation |
| Deep Thinking | `deep-thinking.agent.md` | Cross-cutting architectural analysis |
| Modernization | `modernization.agent.md` | Repo-wide modernization planning |
| DDD | `ddd.agent.md` | Domain-Driven Design modeling and review |

## Copilot Agent Format

VS Code Copilot agents use `.agent.md` with YAML frontmatter:

```markdown
---
name: My Agent
description: What this agent does
model: Claude Sonnet 4.5
tools: ['edit', 'search/codebase', 'myMcpServer/*']
agents: ['*']
handoffs:
  - label: Next Step
    agent: agent
    prompt: Continue from here.
---

System prompt instructions...
```

### Key Frontmatter Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Display name (falls back to filename) |
| `description` | string | Shown as placeholder in chat input |
| `model` | string/array | AI model (e.g. `claude-sonnet-4-6` or `['claude-opus-4-7', 'gpt-4o']`) |
| `tools` | string[] | Tool IDs: `'edit'`, `'search/codebase'`, `'web/fetch'`, `'<mcp-server>/*'` |
| `agents` | string[] | Available subagents (`['*']` = all, `[]` = none) |
| `user-invocable` | boolean | Show in agent dropdown (default: true) |
| `handoffs` | object[] | Suggested transitions to another agent |
| `hooks` | object | Agent-scoped hooks (preview) |

## Naming Convention

- Filename: `{domain}.agent.md` (kebab-case, no `-specialist` suffix)
- `name:` field: Title Case version of the filename (e.g., `backend-python` → "Backend Python")
- No redundant suffixes — the directory is already called `agents/`

## Design Principle: Claude vs Copilot Agents

| Tool | Role | Pattern | Examples |
|------|------|---------|----------|
| Claude Code (`.claude/agents/`) | Workflow modes | Verb-based roles (things you *do*) | reviewer, writer, refactorer, researcher |
| VS Code Copilot (`.github/agents/`) | Domain specialists | Noun-based areas (things you *know*) | backend-python, database, security, ddd |

Both tools share skills from `.github/skills/` and path-scoped rules/instructions for guidance.

## Related

- **Claude Code agents**: `.claude/agents/` (7 agents: architect, code-reviewer, devops, frontend-reviewer, refactorer, researcher, test-writer)
- **Skills**: `.github/skills/` (shared between Claude Code and VS Code Copilot)
- **Instructions**: `.github/instructions/` (auto-loaded by `applyTo:` patterns)
- **Claude Code docs**: <https://code.claude.com/docs/en/sub-agents>
