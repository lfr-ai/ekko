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
  symbol correspond. A behavioral module (port, client, repository, store,
  handler, orchestrator, service, manager, config, container) carries the
  layer role as a class-name suffix. Drop the suffix from the filename **only**
  for a strict Port<->Adapter pair whose bare concept name is unique in the
  tree — the folder pairing (`ports/<role>/x.py` <-> its one
  `infrastructure/.../x.py` adapter) already disambiguates the two files, and
  nothing else in the repo shares that bare name: `ports/repositories/order.py`
  -> `OrderRepositoryPort` (adapter `infrastructure/persistence/repositories/
  order.py` -> `OrderRepository`); `ports/clients/chat.py` -> `ChatClientPort`
  (adapter `ChatClient`); `ports/stores/session.py` ->
  `SessionStorePort` (adapter `SessionStore`). **Keep** the
  full suffix in the filename everywhere the bare concept name recurs across
  3+ layers under a *different* role — dropping it there would create a
  same-named, different-purpose file collision instead of resolving one:
  `account` is a `Port` + a `Repository` + a `Service`, so all
  three keep the suffix (`account_service.py`, never bare
  `account.py`, which would collide with the port/adapter pair's own
  `account.py`); `checkout` is a presentation route
  (`routes/checkout.py`) *and* an orchestrator, so the orchestrator stays
  `checkout_orchestrator.py`; `expiry` is a core policy *and* a
  handler, so the handler stays `expiry_handler.py`. This is why
  `application/handlers/`, `application/orchestrators/`, and
  `application/services/` keep the full role suffix in every filename even
  though each folder already names the role — the folder alone doesn't rule
  out a same-named sibling role elsewhere in the tree the way a strict
  Port<->Adapter pair does. Before dropping a suffix, search the repo for the
  bare candidate stem; if any other file would share it, keep the suffix. A
  port class living under a role-named `ports/<folder>/` subfolder always
  carries that folder's role word before the `Port` suffix, matching its
  adapter's own name (see the three pairs above). The port always needs the
  extra `Port` marker (Python has no `interface` keyword, so a `Protocol`
  class is otherwise indistinguishable from a concrete class); the adapter
  never needs a generic `Adapter`/`Impl` suffix — its own role word is enough,
  and multiple adapters for one port are told apart by a specific descriptor
  prefix instead (`SqlAlchemyOrderRepository`, `FakeOrderRepository`).
  Group only cohesive data types (DTOs, enums, models, value objects, a Port's
  own Record/Payload types) by theme in one module — never two or more
  unrelated behavioral components.
- Mark non-public modules, classes, and helpers as internal (Python: a single
  leading underscore); keep the public API underscore-free. A private module
  or class name must never appear in a package `__all__`.
- Docstrings, including module and `__init__` docstrings, follow the docstring
  rules in `python-conventions`: triple-quoted, concise, and never opening with
  "Return/Response/Request/Payload".
- Use the project's ubiquitous language (see `PROJECT.md`): reuse the exact domain
  nouns in code, tests, and docs — never a near-synonym.

## Structure

- Place code in the layer that matches its role; respect the inward dependency rule.
- Co-locate related files (module + types + tests). Keep folders shallow.
- A new folder mirrors the sibling it most resembles.
- After adding, renaming, or moving modules or folders, refresh the code graph
  with the repository-specific command documented in `PROJECT.md`.

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

## Verification

Symbol-level naming (classes, functions) is ruff/Biome's job; filesystem naming
and class/filename correspondence are not. Two standalone scripts provide
manual audits for that gap; they are not currently wired into the Taskfile,
pre-commit, or CI:

`scripts/check_naming.py` checks Python files/packages are snake_case and
frontend `.ts`/`.tsx` files are kebab-case:

```shell
uv run python .agents/skills/consistency/scripts/check_naming.py [path ...]
```

Defaults to scanning `src`, `tests`, `backend/src`, `backend/tests`,
`backend/alembic`, `scripts`, `tools`, `registry`, and `frontend/src` (when
present) when no path is given.

`scripts/check_class_file_naming.py` checks the class-naming rules above —
a single-public-class behavioral module is named after its class (suffix-aware),
2+ behavioral classes never share one file, `__all__` never exports a
private name, and a `*Port` class under `ports/<clients|repositories|stores>/`
always carries that folder's role word before the `Port` suffix:

```shell
uv run python .agents/skills/consistency/scripts/check_class_file_naming.py [path ...]
```

Defaults to scanning `src`, `backend/src`, `backend/alembic`, `scripts`, `tools`,
and `registry` (when present) when no path is given. Both exit `0` on no
violations.
