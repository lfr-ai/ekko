---
paths:
  - "**/*.md"
---

# Markdown Conventions

Formatting and syntax for every `.md` file. Prose quality (structure, brevity,
no AI boilerplate) lives in the `documentation` skill; *when* to update docs
lives in `update-docs-on-code-change`. This file governs the mechanics.

## Structure

- One `#` H1 per file as the first content line; nest headings one level at a
  time (`#` -> `##` -> `###`), never skipping a level.
- Use ATX headings (`##`), never Setext underlines. Leave one blank line above
  and below every heading, list, table, and fenced block.
- Prefer short sections under descriptive headings over long prose walls.

## Code and data

- Fence every code block with a language tag (` ```python `, ` ```ts `,
  ` ```bash `, ` ```json `); use ` ```text ` when none applies. Never use
  indent-only code blocks.
- Use tables for structured key/value or comparison data — a header row, a
  separator row, then one record per line.
- Wrap inline code, filenames, commands, env vars, and identifiers in backticks.

## Links and images

- Use descriptive link text, never a bare URL or "click here"; angle-bracket a
  URL that must render literally (`<https://example.com>`).
- Link inside the repo by relative path (`../foo/bar.md`), never an absolute
  filesystem path; verify the target exists.
- Give every image meaningful alt text (`![alt text](path.png)`).

## Front matter

- Use YAML front matter (`---`) only where a tool consumes it (an instruction's
  `applyTo`, a skill's `name`/`description`, a prompt's metadata). Keep only the
  fields the consuming tool reads.
