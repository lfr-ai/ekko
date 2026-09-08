---
name: consistency
description: Enforce naming, structure, terminology, and convention consistency across the codebase. Use when adding or renaming files, creating folders, reviewing conventions, or checking that new code matches existing patterns.
---

# Consistency & alignment

Keep the codebase uniform — matching names, structure, terminology, and
conventions — so nothing looks bolted on. Always check new work against what
already exists before adding it.

## Before adding or changing code

1. Find the nearest existing example (same layer or folder) and mirror its shape:
   file layout, naming, imports, error handling, and test structure.
2. Reuse existing names and terms; never invent a synonym for an existing concept.
3. Match the established formatter and linter output — never hand-format against it.

## Naming

- Files: follow the language convention already in the tree (Python
  `snake_case.py`; TypeScript `kebab-case.ts(x)`). Never mix styles within a
  language.
- Folders: lowercase, matching the file convention (Python `snake_case` packages,
  TypeScript `kebab-case`); name them for the concept they hold, not a category.
- Types and classes: `PascalCase`. Functions, methods, and variables: the language
  default (`snake_case` in Python, `camelCase` in TypeScript). Constants:
  `SCREAMING_SNAKE_CASE` — internal (underscore-prefixed) constants carry no type
  annotation.
- One primary public export per file; name the file after it so filename and
  symbol correspond. Group only cohesive data types (DTOs, enums, models) by theme.
- Mark non-public modules, classes, and helpers as internal (Python: a single
  leading underscore); keep the public API underscore-free.
- Docstrings, including module and `__init__` docstrings, follow the docstring
  rules in `coding-conventions`: triple-quoted, concise, and never opening with
  "Return/Response/Request/Payload".
- Use the project's ubiquitous language (see `PROJECT.md`): reuse the exact domain
  nouns in code, tests, and docs — never a near-synonym.

## Structure

- Place code in the layer that matches its role; respect the inward dependency rule.
- Co-locate related files (module + types + tests). Keep folders shallow.
- A new folder mirrors the sibling it most resembles.
- After adding, renaming, or moving modules or folders, refresh the code graph
  (`task graph`) so code intelligence stays accurate.

## Conventions and word usage

- Follow the scoped rules under `.github/instructions/` and `.claude/rules/`.
- Keep terminology identical across code, tests, docs, and specs.
- Prefer the existing pattern over a new abstraction unless duplication is clearly
  wrong.

## Agentic-setup consistency

Alignment across the `.github`, `.claude`, and `.agents` trees is governed by the
`agent-config` skill and enforced by the agent-config guard (skill parity,
portability, byte-identical skills, and MCP parity). Run the guard after touching
any agent configuration.
