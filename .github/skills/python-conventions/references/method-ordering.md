# Method and function ordering

Neither PEP 8 nor the Google Python Style Guide prescribes member order — pick
a **logical order a maintainer could explain**, never "chronological by date
added" (the one explicit rule Google's Java Style Guide states for this exact
question — §3.4.2, "new methods are not just habitually added to the end of
the class ... which is not a logical ordering" — and it generalizes past Java).
This project applies two distinct, direction-opposite conventions depending on
scope, both mechanically enforced by
[`scripts/check_method_ordering.py`](../scripts/check_method_ordering.py)
(wired into `task guard`).

## Class scope: top-down stepdown

`__init__` → alternate constructors (`from_config`, other
`@classmethod`/`@staticmethod`) → then each public method immediately
followed by the private helper(s) used only by it (Clean Code's "stepdown
rule" — read top-to-bottom like a newspaper, most-abstract first, the same
Locality of Behavior principle applied to member order).

**Worked example** — `ChatClient` (`infrastructure/clients/chat.py`):
`_completion_kwargs` sits directly above the two `query_*_async` methods that
call it, not banished to a separate "private methods" block at the bottom.

Do not sort a class into a public-block-then-private-block layout — it
scatters a helper away from its only caller and forces the reader to jump. A
helper shared by several public methods anchors near `__init__` or its first
caller instead. Method overloads and multiple constructors stay grouped
together, never split by an unrelated member placed in between.

## Module scope: bottom-up definition-before-use

Among **top-level functions** in a module (a script, a CLI entry point, a
function-only utility module, or the module-level functions in a file that
also defines a class), the direction is the opposite of class scope: a
private helper is defined **before** the function that calls it, building up
from small pieces to the module's entry point at the very bottom, directly
above any `if __name__ == "__main__":` guard. This matches the Google Python
Style Guide's own "Main" convention (`def main(): ...` followed by the guard)
and is the natural fit for Python, where the reader encounters small pieces
before the thing that composes them — the same "leaves before the composing
root" order the `Container` DI composition root
(`composition/container.py`) already uses for its `@cached_property` chain.

**Worked examples**:

- `prompts/cli/_list.py`: `_template_version` (private) sits directly above
  `collect_status`, its one caller.
- `infrastructure/clients/document_loader.py`: `_load_with_ntlm` sits
  directly above `_load_remote_ntlm_document`, its one caller; the unrelated
  `_load_remote_http_document` path is grouped separately, not sandwiched
  between a helper and its caller.
- `main.py`, `scripts/backtest/main.py`, `prompts/cli/__main__.py`: every
  `_register_*`/`_run_*` helper precedes the `create_app`/`main` function that
  wires them together, which sits last in the file.

### Dispatcher/registry exception

A function that fans out to **more than a handful of** independent
single-caller helpers (a CLI `main()` dispatching to a dozen `_check_*`
validators, in `.agents/guard/verify_agent_config.py`) is a dispatch table,
not a 1:1 stepdown extraction — its handlers do not need to sit literally
adjacent to it. Group them by topic/concern instead (with a blank line or
short comment banner per group) and keep the entry point last. The checker
recognizes this pattern (more than 3 direct single-caller helpers) and does
not flag it.

## Multiple classes or a class-plus-functions in one file

The Google Python Style Guide explicitly allows this ("Place related classes
and top-level functions together in a module" — unlike Java's one-class-per-
file rule); order it by **dependency/usage**, never alphabetically:

- **Supporting module-level functions/`Protocol`s before the class(es) that
  use them** — `infrastructure/clients/chat.py`: `_is_reasoning_model`,
  `_build_messages`, and the `_ChatConfig`/`_ChatProviderConfig` `Protocol`s
  all precede `ChatClient`, the class that uses them.
- **Base/mixin before the classes that extend it** —
  `infrastructure/persistence/orm/models.py`: `ORMBase` → `_CreatedOnMixin` →
  `_TimestampMixin` → the concrete entity classes (`Customer`, `Order`, …).
- **The core domain type before the DTOs that wrap or extend it** —
  `application/dtos/order/order.py`: `Order` (the internal representation)
  precedes `OrderCreateRequest`/`OrderCreateResponse`/`OrderOrchestrateRequest`/
  `OrderOrchestrateResponse` (the request/response shapes built from or
  producing it).
- A small private snapshot dataclass a repository converts to/from
  (`_OrderRecordSnapshot` + `_to_order_record` in
  `infrastructure/persistence/repositories/order.py`) precedes the repository
  class that uses it, following the same bottom-up module rule above.

## Function-only modules (scripts, CLI utilities)

Apply the module-scope bottom-up rule exactly as above: helpers first, the
module's public entry function (or, for a script, `main()`) last, directly
above the `if __name__ == "__main__":` guard when present.
