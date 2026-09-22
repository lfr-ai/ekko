---
name: "Commit Message"
description: "Generate a Conventional Commits 1.0.0 message for the current change set. Read-only — never runs git; outputs the message for you to commit manually."
category: "Version control"
tags: ["git", "commit", "conventional-commits", "changelog"]
---

Produce a single [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/#specification)
message for the current change set.

## Constraints

1. **Never run `git`.** Do not stage, commit, or invoke `git` in any form. Infer
   the change from the diff and files already in context; if it is unclear, ask
   which files to describe rather than guessing.
2. **Match the repo's Commitizen setup** (`cz_conventional_commits` in `.cz.toml`):
   use the standard types only, so `cz`/`commitizen` and the changelog stay valid.
3. **Output only the message**, in one fenced block ready to paste — no prose
   before or after unless asked.

## Format

```text
<type>(<scope>)<!>: <description>

<body>

<footer(s)>
```

- **type** — one of `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`,
  `build`, `ci`, `chore`, `revert`.
- **scope** — optional short noun for the area (`api`, `persistence`, `ai`,
  `config`, `frontend`, …); omit when the change spans many.
- **description** — imperative mood, lower case, no trailing period, ≤ ~72 chars.
- **body** — optional; explain motivation and what changed, wrapped ~72 cols —
  not a line-by-line restatement of the diff.
- **footers** — optional; `BREAKING CHANGE: <detail>` (or `!` after type/scope)
  for incompatible changes, plus issue refs like `Refs: #123`.

## Rules

- One logical change per commit; if the diff mixes concerns, propose separate
  messages instead of one vague commit.
- Use `!` / `BREAKING CHANGE:` only for real public-contract breaks.
- Prefer `fix` for bug fixes and `feat` for new behavior; use `chore`/`build`/`ci`
  for non-shipping changes.
- Be terse and truthful — never invent changes that are not in the diff.
