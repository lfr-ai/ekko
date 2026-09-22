---
name: "Align Conventions"
description: "Analyze the whole codebase, then align and enforce ALL project conventions — naming, structure, clean-architecture, docstrings, typehints, cognitive load, and minimalism (omit redundant defaults) — across every layer, behavior-preserving and gate-verified. Exhaustive, plan-driven."
category: "Conventions"
tags: ["conventions", "clean-architecture", "refactor", "naming", "typing", "cognitive-load", "quality"]
---

Enforce the project's conventions across the entire codebase — align every module
to the naming, structure, clean-architecture, docstring, typing, cognitive-load,
and minimalism rules the repo already defines.

**Scope (optional):** If a scope is given (a layer — `config`, `core`, `ai`,
`infrastructure`, `application`, `presentation`, `composition`, `cli` — or a path
under the backend source package, see `PROJECT.md`), restrict the walkthrough to
it. Otherwise cover the
whole source package (named in `PROJECT.md`), then `scripts/`, migrations, and
`tests/`.

## Non-negotiable constraints

1. **The conventions are the spec.** Canonical sources, in order: `AGENTS.md`
   (Hard Rules), `.github/instructions/*.instructions.md` and the paired
   `.claude/rules/*`, then the skills (`python-conventions`, `consistency`,
  `clean-architecture`, `ddd`, `configuration`, `database-migrations`,
  `api-contracts`, `documentation`, `cognitive-load`). Project facts come from
  `PROJECT.md`. When rules disagree, `AGENTS.md` wins.
2. **Behavior-preserving.** Refactor to the conventions WITHOUT changing runtime
   behavior, public contracts, or test outcomes. If a fix would change behavior,
   do NOT force it — record it under "Behavioral risks (out of scope)".
3. **Toolchain: uv + Task only.** Use `task` and `uv run`. Never `pdm`, `poetry`,
   `pipenv`, `conda`, `pip`, or bare `python`/`pytest`.
4. **No `git` commands.** All version-control actions are the user's.
5. **Enforce in place; do not add abstractions.** No new wrappers, shims, or
   compatibility layers. Removing dead code and legacy shims IS in scope.

## Phase 1 — Comprehensive codebase analysis & review

- Map the architecture layers (see `PROJECT.md`) and confirm dependencies flow
  inward only.
- Inventory the public surface per layer: modules, classes, ports/protocols,
  DTOs, value objects, enums, handlers, repositories, routes.
- Use `semantic_search`, `grep_search`, `file_search`; if GitNexus is available
  use it for call-graph and impact context before any rename.

## Phase 2 — Convention inventory (what to enforce)

Catalog every deviation, grouped by rule family:

- **Type safety** — no `Any`; no `cast`; no string-literal forward refs (use
  `from __future__ import annotations`); `X | None` not `Optional`; lowercase
  builtins (`list`/`dict`/`tuple`) not `List`/`Dict`.
- **Docstrings** — triple-quoted always; summaries never start with
  `Return/Returns/Response/Request/Payload`; typed `Args`/`Returns`/`Yields`/
  `Raises`; `Raises` lists only exceptions raised directly; property docstrings
  are noun-phrase one-liners (no `Returns:`); route handlers one-line when the
  decorator supplies `description=`; `DTO`/`DTOs` as the acronym (expanded once
  only, in the `dtos` package docstring); no `-> None` on `__init__`/
  `__post_init__`. Beyond
  properties, apply the same brevity test to every function: drop `Args`/
  `Returns` when they only restate a parameter/return type already visible in
  the signature; keep (or add) a section only when it carries real
  caller-relevant meaning the signature can't — a non-obvious constraint, a
  return value whose meaning isn't the type alone, or `Raises` for any
  exception the caller must anticipate.
- **Polymorphism** — flag a growing `isinstance`/type-tag `if`/`elif` or
  `match` chain on an object's *type* (not a closed, self-owned `StrEnum`) as
  an Open/Closed smell; replace with a `Protocol`-based Strategy per the
  `python-conventions` skill's `references/polymorphism-patterns.md`. Do not
  introduce an abstraction for a single existing implementation — that is
  speculative generality, not a fix.
- **Logging** — `import logging` with module-qualified members; the module logger
  is `_logger = logging.getLogger(__name__)`.
- **Imports & `__init__.py`** — qualified-vs-direct policy per package (never
  both styles for one package); first-party symbols imported directly;
  `__init__.py` is a docstring-only namespace OR a re-export hub (`__all__`
  bijection, isort-sorted) — never implementation code (only the root package
  carries dunder metadata + app-identity constants).
- **`@final` / `@override`** — `@final` on composed behavioral components
  (handlers, orchestrators, services, clients, repositories, stores, metrics,
  manager, container, per-env configs); `@override` on every real override
  (ABC/`@abstractmethod` impls, framework overrides, and each port/adapter
  method). Skip both on data/value types, DTOs, enums, `NamedTuple`s, framework
  adapters (middleware, logging filters/formatters), ABCs/Protocols/bases, and
  internals.
- **Naming & prefixes** — internal (`_`) for non-public modules/classes/helpers/
  constants; one public class per behavioral module with filename ↔ concept;
  layer-role suffixes (`Port`/`Client`/`Repository`/`Store`/`Settings`/`Config`/
  `Handler`/`Orchestrator`/`Service`/`Manager`); a `*Port` class under
  `ports/<clients|repositories|stores>/` always carries that folder's role word
  before `Port` (`ChatClientPort`, not bare `ChatPort`) — the adapter carries
  only its own role word, never a generic `Adapter`/`Impl` suffix; acronyms
  fully upper (`HTTPLogger`); `SCREAMING_SNAKE_CASE` constants (internal ones
  untyped).
- **Custom-type tiers** — pick the lightest that fits: validated value object
  (enforceable boundary invariant) → structural/decoupling `type` alias →
  `NewType` (opaque id) → bare primitive. Never a scalar alias for documentation
  only.
- **Config & `from_config`** — `*Settings` own env-sourced fields; `*Config` is
  the assembled object or a consumer view of it; components expose
  `from_config(cls, config: _XConfig)` with a private structural `Protocol` in
  the same module, never importing the aggregate config.
- **Annotated-first metadata** — `Annotated[...]` for FastAPI/Pydantic metadata;
  assignment form only when `default`/`default_factory`/`alias` require it.
- **Dataclass intent** — `kw_only=True` on every dataclass; value-like objects
  add `frozen=True, slots=True`.
- **Clean-architecture boundaries** — core is stdlib-only (plus Pydantic schema
  dunder hooks in scalar/value modules); infrastructure never imports
  application; presentation reaches the container only through structural
  protocols.
- **Database access** — persistence frameworks stay in infrastructure; session
  scope and transaction ownership are explicit; values are bound rather than
  interpolated; ordering is deterministic; indexes are evidence-driven; Alembic
  candidates are reviewed and upgrade/downgrade/drift behavior is verified.
- **AI provider boundary** — provider SDK imports stay in the exact
  infrastructure model-client modules allowed by the boundary test; application
  code depends on ports; LiteLLM kwargs, secrets, retries, structured output, and
  reasoning-model differences remain localized and tested.
- **Cognitive load** — extract complex booleans into named variables; early
  returns over deep nesting; deep modules over shallow wrappers; keep
  tightly-coupled logic together.

## Phase 3 — Research (web + documentation)

- Use Context7 (`mcp_context7_*`) for version-accurate docs (Pydantic, FastAPI,
  SQLAlchemy, Alembic, litellm) and the relevant PEPs (8 naming, 484/604 typing,
  544 protocols, 591 `final`, 698 `override`). Cite sources in the plan.

## Phase 4 — Extensive TODO / PLAN

- Write a checkable plan BEFORE editing, grouped by layer then file. For each item
  note the deviation, the fix, and the risk. Keep "Behavioral risks (out of
  scope)" separate. Maintain it as a living checklist and tick items off.

## Phase 5 — Systematic walkthrough (execute, inward-out)

Work layer-by-layer in dependency order — `config → core → {ai | infrastructure}
→ application → presentation → composition → cli`, then `scripts/`,
`backend/alembic/`, `tests/`. Per file, apply the Phase 2 checklist, and:

- Use the language-server rename (not find/replace) for symbol renames; update
  every call site and `__all__` in the same change-set.
- Remove dead code (unused methods, constants, imports, stale helpers) as you go.
- After each module or logical group, re-check just that file
  (`uv run ruff check <path>`, and `uv run ty check <path>` where practical).

## Phase 6 — Minimalism pass (omit redundant defaults)

Strip anything that restates a default or adds noise without safety:

- No `-> None` on `__init__`/`__post_init__` (the implicit `None` is understood).
- Drop dataclass/decorator arguments that restate the library default
  (`frozen=False`, `eq=True`, `init=True`); keep intent-bearing flags such as the
  required `kw_only=True`.
- Prefer the simplest declaration that preserves behavior — e.g.
  `field: X | None = None` over `Field(default=None)` when no other `Field`
  metadata is needed.
- No `Final` on internal (`_`) constants, and no type annotation on internal
  constants at all; reserve `Final[...]` for public module constants.
- No redundant re-export aliases; no scalar `type` alias that only documents.
- Remove backward-compat shims, alias modules, and deprecated wrappers; update
  call sites instead.
- Choose the shortest correct form (early return, comprehension, `X | None`) that
  still reads clearly — never trade cognitive load for brevity.

## Phase 7 — Full validation (iterate until clean)

Run `task lint`, `task typecheck`, `task test`, and `task check`. The final
`task check` executes all configured pre-commit and agent-config parity guards.

- For `@override` completeness, run a one-off explicit-override check (mypy
  `--enable-error-code explicit-override`, if available); `ty` does not flag a
  *missing* `@override`.
- Introduce NO new `ty`/`ruff` diagnostics. Pre-existing baseline items unrelated
  to the change stay untouched unless the user asks otherwise.

## Definition of done

- Every in-scope file complies with the conventions above; no behavior changed.
- No `Any`/`cast`/quoted forward refs; docstrings, logging, imports, `final`/
  `override`, naming, custom-types, config, and dataclasses all conform.
- Redundant defaults omitted; dead code and legacy shims removed.
- Validation gates green (or only pre-existing, unrelated baseline noise remains —
  reported explicitly). Zero `git` commands run.

## Final report

End with a concise `tldr;`:

- Per-layer / per-file changes (deviation found → fix applied).
- Behavioral risks found (out of scope) with location and expected vs actual.
- Any pre-existing baseline items left untouched, and why.
- Final validation output (ruff, ty, guard, and test counts).
