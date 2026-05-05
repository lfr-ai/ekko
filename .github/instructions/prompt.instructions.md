---
applyTo: "**/*.prompt.md"
---

# Prompt File Guidelines

Prompt files (`.prompt.md`) are reusable Copilot prompts under `.github/prompts/`.

## Frontmatter

Every prompt file must have:

```yaml
---
description: One sentence describing what this prompt does
name: prompt-name
argument-hint: 'Optional: description of expected argument'
agent: ask   # or: auto, current
model: 'Claude Sonnet 4'
tools:
  - read/readFile
  - search/codebase
  - edit/editFiles
---
```

## Structure

1. **Title** — H1 matching the `name` field
2. **Purpose** — one sentence on when to use this
3. **Steps** — numbered, each with a bash command or code block
4. **Conventions** — project-specific rules the agent must follow

## Tool Reference

| Tool ID | Purpose |
|---------|---------|
| `read/readFile` | Read file contents |
| `search/codebase` | Semantic code search |
| `search/textSearch` | Grep-style text search |
| `search/usages` | Find symbol usages |
| `edit/editFiles` | Create or modify files |
| `execute/runInTerminal` | Run shell commands |
| `execute/getTerminalOutput` | Read terminal output |

## Rules

- Keep prompts focused on a single workflow
- Include concrete bash commands, not vague instructions
- Reference project-specific paths (e.g. `tests/unit/`, `backend/src/ekko/`)
- Always end with a verification step
