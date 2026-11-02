# Dunder files and methods

Loaded on demand from `python-conventions/SKILL.md` — read when writing a
`__dunder__` method or a package `__init__.py` / `__main__.py`.

## Dunder files

- `__init__.py` — see the SKILL's "Package Exports" section: one-line docstring;
  a namespace package is docstring-only; a re-export hub is docstring + explicit
  imports + an isort-sorted `__all__` that is a bijection with the imports. No
  implementation code (sole exception: the root package owns dunder metadata
  such as `__version__`).
- `__main__.py` — the `python -m package` entry point. Keep it a thin
  `def main() -> None:` plus `if __name__ == "__main__": main()`; put real logic
  in an imported module so it is testable without spawning a subprocess.
- `__all__` — a list (never a tuple), isort-sorted, holding exactly the public
  names (ruff `RUF022` + `F401`).

## Constructor dunders

- `__init__` — no `-> None` annotation (Hard Rule 7); no docstring when it takes
  zero real params, else a full `Args:`. Behavioral classes write an explicit
  `__init__`; data classes use `@dataclass` and never hand-write one.
- `__new__` — only for a value object subclassing an immutable built-in
  (`int` / `str` / `float`); validate, then `return super().__new__(cls, value)`.
  A single value parameter is positional-only (`/`) — see
  `signature-patterns.md`. Never `@override` `__new__` / `__init__`.
- `__post_init__` — a `@dataclass`'s validation hook; no `-> None`; raise
  `ValueError` / `TypeError` on an invariant breach. Do not reassign frozen
  fields (`object.__setattr__` only as a documented last resort).

## Value and identity dunders

- A `@dataclass` generates `__eq__` / `__repr__` (and `__hash__` when
  `frozen=True`) — do not hand-write them. If you write `__eq__` by hand you MUST
  also define `__hash__` (or set `__hash__ = None`); the two always travel
  together.
- `__slots__` — set via `@dataclass(slots=True)`; on a hand-written class use
  `__slots__ = ("_x", "_y")`. A `str` / `int` subclass value object uses
  `__slots__ = ()` to stay zero-overhead. `__slots__` conflicts with
  `@cached_property` — see the SKILL's "Caching" note.
- `__repr__` — let the dataclass generate it; hand-write only to redact a secret,
  personal identifier, or large payload, never to restate the default. Preserve
  the type name and mask the value (for example,
  `return f"{type(self).__name__}('******-****')"` for a national-ID-like
  identifier); do not make a redacted representation look reconstructible when
  the masked value would fail validation. For a dataclass field containing a
  secret, personal data, or a potentially large payload, prefer
  `field(repr=False)` so the generated representation remains useful without
  copying the payload into logs or tracebacks.

## Protocol and framework dunders

- `__get_pydantic_core_schema__` / `__get_pydantic_json_schema__` — add to a
  value object only when it is used as a Pydantic model field; keep them
  classmethods returning the handler-built schema (see `framework-patterns.md`).
- `__call__` — define only for a genuine callable object (a callback protocol, a
  configured strategy); a single-method class is usually clearer as a named
  method.
- Context managers — pair `__enter__` / `__exit__` (or `__aenter__` /
  `__aexit__`); prefer `contextlib.contextmanager` / `asynccontextmanager` for
  simple cases.

## Avoid

- `__del__` — finalizer timing is unreliable; use a context manager or an
  explicit `close()` / `dispose()` instead.
- `__getattr__` / `__setattr__` magic on a normal class — it defeats type
  checking and readers; reach for it only at a genuinely dynamic boundary.
- Name-mangling `__x` (two leading, at most one trailing underscore) — use a
  single `_x` for non-public members; reserve `__x` for real subclass-collision
  avoidance only.
