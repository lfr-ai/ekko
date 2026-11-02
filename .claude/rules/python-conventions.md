---
paths:
  - "**/*.py"
---

# Python Conventions

Full worked examples, templates, and the enforcement script live in the
`python-conventions` skill (`.agents/skills/python-conventions/SKILL.md`) —
pull it up for deep patterns. `AGENTS.md` Hard Rules 1-8, 14-17, 20 cover
the type-safety/dataclass/logging/configuration baseline this file extends.

## Imports

One style **per package**, applied everywhere (classes and functions alike);
never mix within a package (ruff `ICN`). The full per-module lists live in the
`python-conventions` skill.

- **Direct** (`from x import Y`): stdlib type/data modules (`typing`,
  `collections.abc`, `dataclasses`, `enum`, `pathlib`, `datetime`, `functools`),
  distinctive framework symbols (`pydantic.BaseModel`, `fastapi.FastAPI`),
  first-party `myapp.*`.
- **Qualified** (`import x` → `x.Y`): generic-named stdlib utilities (`logging`,
  `os`, `json`, `re`, `asyncio`) and namespace-heavy or aliased third-party
  (`httpx`, `litellm`, `numpy as np`). Tests/tools may use
  `import myapp.main as main_module` for monkeypatching.

## Package Exports (`__init__.py`)

One-line module docstring on every package. Namespace packages: docstring
only, no imports/`__all__`. Re-export hubs: docstring + `from … import …` +
an isort-sorted `__all__` that is a bijection with the imports. No
implementation code in `__init__.py` (sole exception: the root package
`__init__.py` owns dunder metadata). Enforced by ruff `RUF022` + `F401`.

## Type Safety

Hard Rules 1-3, 6, 7 (no `Any`/`cast`/quoted refs; `from __future__ import
annotations`; typed docstring sections; no `-> None` on `__init__`/
`__post_init__`) and Hard Rule 16's 5-tier scalar classification apply
directly — define shared custom types in `core/types.py`. Enums extend
`StrEnum` (textual/wire values) or `IntEnum` (numeric identity matters);
decorate `@unique`; generate values with `auto()`.

## Dataclasses

`kw_only=True` on every dataclass (Hard Rule 4); `frozen=True, slots=True`
for immutable/value-like classes. Use `@dataclass` only for data-holding types
(value objects, DTOs, events, `*Settings`/`*Config`); behavioral components
(adapters, repositories, orchestrators, services, the DI container) stay plain
classes with an explicit `__init__`. Prefer `@property` for computed attributes.
See the `python-conventions` skill "Dataclass vs. plain class" and "Caching"
for the decision rule and the `@cached_property`/`slots` interaction.

## Function Signatures

Use a `*` keyword-only separator once a function has 3+ parameters; 1-2 may
stay positional. Add a `/` positional-only separator (PEP 570) when a
parameter's name carries no external meaning beyond "the value" — even for
one argument (`MaxTokens.__new__(cls, max_tokens: int, /)`,
`from_config(cls, config, /)`). Never add `/` to a domain-noun/framework param;
a single-argument port/repository query method stays keyword-only
(`get_by_id(*, user_id)`). Full vocabulary: `references/signature-patterns.md`.

## `@final` / `@override`

Import both from `typing` (never `typing_extensions`); `@final` above `class`,
`@override` above `def`. `@final` seals composed service classes and methods
subclasses must not override; `@override` marks every concrete override of a
subclassed base/`ABC`/`Protocol` member. Default to a `Protocol` port +
`@override`-decorated adapters; reach for `ABC` only when adapters share real
executable code. Full placement/pattern matrix: `references/polymorphism-patterns.md`.

## Naming and Module Layout

- Single leading underscore marks non-public; public names go in `__all__`. A
  `from_config` view `Protocol` is always private (`_ChatConfig`).
- One public class per behavioral module; the filename is that class in
  `snake_case` and the class name carries its layer-role suffix (`Port`,
  `Client`, `Repository`, `Handler`, `Service`, …). Drop the suffix from the
  filename only for a Port<->Adapter pair whose bare concept name is unique
  in the tree; keep it whenever that bare name recurs elsewhere under a
  different role — full collision-avoidance test in the `consistency` skill.
- Write `DTO`/`DTOs` (never "Pydantic models"/"schemas"); use the exact
  ubiquitous-language nouns from `PROJECT.md` (see the `consistency` skill).
- No magic values: extract a repeated literal to a named constant (ruff
  `PLR2004`, relaxed in `tests/**`). Full matrix: `python-conventions` skill.
- Never write a Java-style `get_x()`/`set_x(value)` pair for plain attribute
  access — use a public field or `@property`; `get_`-prefixed methods are
  reserved for genuine behavior (I/O, a keyed lookup), never a bare `return self._x`.

## Method Ordering

`__init__` → alternate constructors → each public method immediately followed
by its single-use private helper (stepdown rule) — never chronological, never
public-block-then-private-block. Module functions: definition-before-use,
entry point last; multi-class/mixed files order by dependency. Enforced by
`check_method_ordering.py`; full rules: `references/method-ordering.md`.

## Docstrings

Google-style, triple-quoted even for one-liners. Never open a summary with
"Return(s)/Response/Request/Payload/Raised" (Hard Rule 6); `Raises:` lists only
directly-raised exceptions; sections are all-or-nothing; `__init__` takes no
docstring or a full `Args:`, never a bare summary. Worked examples:
`python-conventions` skill + `references/docstring-patterns.md`.

## Error Handling

Catch specific exception types, never a bare `except:`. Preserve context:
`raise ProcessingError(...) from e`, never a bare re-raise discarding the
original. Pass the message straight to the constructor — never bind it to a
`message`/`msg` variable first (`EM` disabled; see ruff.toml). Use named
constants from `fastapi.status` (`status.HTTP_200_OK`), never a numeric literal.

## Annotated-first Metadata (FastAPI + Pydantic)

Prefer `Annotated[..., Query/Path/Body/…/Depends(...)]` (FastAPI) and
`Annotated[..., Field(...)]` (Pydantic); use assignment form only when
`default`/`default_factory`/`alias` need constructor clarity (Hard Rule 14).
Use PEP 695 `type` aliases/generics; reserve `NewType` for opaque ids; reuse
FastAPI dependencies as module-level `Annotated` assignments (see skill's
`references/framework-patterns.md`).

## Async I/O

Never call a blocking method inside `async def` — offload with `await
asyncio.to_thread(fn, ...)` or a native async client; await independent calls
with `asyncio.gather(...)`, not sequential awaits. Cancel/drain sibling tasks
(`asyncio.create_task`) on failure and guard a shared client's refresh with
`asyncio.Lock`. Full patterns: `python-conventions` skill's `references/framework-patterns.md`.

## Configuration & `from_config`

Hard Rule 20: `*Settings`/`*Config` split; a component reads config through a
private structural `_XConfig` Protocol (PEP 544), never importing `AppConfig`.
Cognitive load: see `cognitive-load.md` (auto-loaded alongside
this file for every `.py` change).
