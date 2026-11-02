# Signature and attribute-access patterns

Loaded on demand from `python-conventions/SKILL.md` — read this when choosing
whether a parameter should be positional-only or keyword-only, reviewing a
getter/setter pair for a plain attribute, or picking a verb for a new
function/method name.

## Positional-only `/` (PEP 570)

Add `/` after a parameter whose name carries no external semantic meaning
beyond "the value being wrapped" — the caller gains nothing from naming it,
and the author loses the ability to ever rename it once someone calls it by
keyword. This holds **even for a single argument**: a one-parameter value
object is precisely PEP 570's motivating case (its own example is the
type-conversion `def as_my_type(x, /)`), so the `/` is grounding, not
ceremony.

```python
class MaxTokens(int):
    def __new__(cls, max_tokens: int, /) -> Self: ...


class _StructuredOutput(Protocol):
    @classmethod
    def model_validate_json(cls, json_data: str | bytes | bytearray, /) -> Self: ...
```

Reach for `/` when any of these hold:

- **A scalar value object subclassing a built-in** (`MaxTokens`, `Temperature`,
  `Confidence`, a validated-id wrapper) — the constructor's only job is
  validating and holding one value, so the parameter name just restates the
  class. The `/` mirrors CPython's own positional-only `int`/`str`/`float`
  constructors (keyword calls to `int`/`float`/`bool`/`list`/`tuple` are
  rejected outright), making it the *consistent*, idiomatic choice.
- A method whose signature mirrors a stdlib/third-party contract that is
  itself positional-only (`model_validate_json`, a dunder-style method).
- A base-class method a subclass must not be able to break by renaming the
  parameter in an override (Liskov safety — see PEP 570's "Consistency in
  Subclasses").
- **A single-argument alternative constructor or parse/convert helper** whose
  sole data parameter is a generic placeholder for the source value:
  `from_config(cls, config, /)`, `from_dict(cls, data, /)`,
  `from_optional(cls, value, /)`, `parse_amount(raw_amount, /)`,
  `_coerce_value(raw_value, /)`. The method name already states the
  source kind, so `config`/`data`/`value`/`raw` only restate it — mirroring
  CPython's positional-only `from_*` classmethods (`datetime.fromisoformat`,
  `dict.fromkeys`, `bytes.fromhex` all reject keyword calls).

Do NOT add `/` to a parameter whose name carries real documentation value.
Three cases keep the default positional-or-keyword:

- a constructor/service parameter that names a distinct role
  (`chat_client`, `deployment_name`);
- a **sole parameter named for a domain entity** — `_to_user_record(user)`,
  `_to_order_record(order)` — where the noun tells the reader the input
  type at a glance;
- a **framework-invoked method** whose call the framework owns and never keys
  by name (`@field_validator` classmethods, `__get_pydantic_core_schema__`),
  so `/` would be moot noise.

PEP 570's own rule of thumb: positional-only "if names do not matter or have no
meaning"; keyword-only (via `*`) "when names have meaning and the definition is
more understandable by being explicit".

## Keyword-only `*` for port query methods

The mirror image of the positional-only case: when a single parameter *names a
domain concept the caller looks something up by*, make it keyword-only with `*`
— never `/`. The name carries real meaning, and the method is a cross-boundary
seam (a repository, store, or client port), so a self-documenting call site is
worth the two extra characters.

```python
class _UserRepositoryPort(Protocol):
    def get_by_id(self, *, user_id: UserId) -> User | None: ...
    def get_or_create(self, *, email: str) -> User: ...


class _CacheStorePort(Protocol):
    def pop(self, *, key: str) -> bytes | None: ...
```

Call sites read as prose — `repo.get_by_id(user_id=user_id)`,
`store.pop(key=key)` — and a lookup key can never land in the wrong position.
Apply it to every single-argument method on a repository, store, or client port
(`get_by_*`, `get_or_create`, `fetch`, `pop`, `extract`, a single-key `load_*`).
For a multi-parameter port method, keep the **primary** domain subject
positional and make the secondary/optional parameters keyword-only:

```python
def load(
    self, url: str, *, username: str | None = None, password: str | None = None
) -> Document: ...
```

Do NOT force keyword-only on an **in-layer behavioral method** that takes one
rich aggregate or DTO whose type is self-evident — that stays plain positional,
since naming it would only add noise (`handler.process(order)`, not
`process(*, order=...)`).

The single-argument decision in one line: **`/`** when the name is a generic
placeholder for a value (`value`, `data`, `config`); **`*`** when the name is a
domain key on a cross-boundary port (`user_id`, `email`, `key`); **plain
positional** for one aggregate/DTO passed to an in-layer method (`order`).

## The `raw_` prefix

Prefix a variable or parameter with `raw_` when it holds input that has crossed
a boundary but is **not yet validated, coerced, or normalized** into its typed
domain form — the "as-received" value. Drop the prefix the moment it is
validated: the un-prefixed name denotes the trusted, typed form.

```python
raw_items = data.get("items")  # unvalidated, still `object`
items = [Item.from_dict(x) for x in raw_items]  # validated, typed
```

Reach for `raw_` at boundaries: `@field_validator(mode="before")` inputs
(`raw_value`), deserialized JSON items before conversion (`raw_item`), a secret
before transformation (`raw_password` → `quote_plus` → `password`), external
input before wrapping in a value object (`raw_id` → `UserId(...)`). Prefer
`raw_<noun>` when a noun exists (`raw_password`, `raw_amount`); use `raw_value`
as the generic single-value fallback. Type the raw form loosely (`object`/`str`);
the result gets the precise type. Keep both names in the same scope so the
transformation is visible. Do NOT prefix already-validated domain objects, and
never use `raw_` as a filler for an unnamed value — it must mean "pre-validation".

## Don't name a parameter after a different sibling type

A "generic value" placeholder (`value`, `data`, `moment`) still has to name the
parameter's *own* type, not a same-module sibling type with a different shape.
`datetime.date` and `datetime.datetime` are distinct types — naming a
`datetime`-typed parameter `date` reads as "a calendar date" and misleads a
reader who has `from datetime import date` in scope elsewhere in the same
codebase. Prefer a name that reflects "a point in time" (`moment`) over a
placeholder that collides with an unrelated type name:

```python
# Bad: reads as `datetime.date`, but the annotation is `datetime.datetime`
def format_date(date: datetime, /) -> str:
    return date.strftime(_DATE_FORMAT)


# Good: `moment` names the value as an instant in time, matching `datetime`
def format_date(moment: datetime, /) -> str:
    return moment.strftime(_DATE_FORMAT)
```

Apply the same check whenever a placeholder name also names an unrelated
builtin or frequently-imported stdlib type (`list`, `type`, `id`, `set`,
`object`, `hash`) — pick a synonym before shipping.

## Attribute access: no Java-style getters/setters

```python
# Bad: Java-style accessor pair for a plain attribute
class Order:
    def get_total(self) -> Decimal:
        return self._total

    def set_total(self, value: Decimal) -> None:
        self._total = value


# Good: property (mutable) or a plain field (dataclass/frozen)
class Order:
    @property
    def total(self) -> Decimal:
        return self._total

    @total.setter
    def total(self, value: Decimal) -> None:
        self._total = value
```

A `get_`-prefixed method name is reserved for genuine behavior a plain
attribute read cannot express — I/O, a keyed lookup, an expensive
computation, or database access (`get_by_id`, `get_or_create`, `get_session`
on a repository/store port). If the method body is a bare `return self._x`
(or a bare assignment for a setter), it is an accessor pair in disguise —
replace it with `@property`. PEP 544 rejected forcing getters/setters where a
plain variable would do as "quite unpythonic"; a validating `@property` setter
is the sanctioned seam when a write genuinely needs to enforce an invariant.

## Verb vocabulary for function/method names

One verb, one meaning, everywhere — never pick a synonym because it "sounds
better" for one call site. Before naming a new function, match it to the
narrowest row below; do not introduce a new verb for a shape already covered.

| Verb | Meaning | Shape | Example |
|------|---------|-------|---------|
| `get_*` | Genuine behavior only — I/O, keyed lookup, computation. Never a bare `return self._x` (see above). | sync | `get_by_id`, `get_or_create`, `get_session` |
| `load` | Read a resource from an addressable, known-shape source into a typed value. | sync | `DocumentLoaderClientPort.load(url)`, `load_composed_prompt` |
| `fetch` | Retrieve a resource across a remote/network boundary by identifier. | async | `DocumentRetrieverClientPort.fetch(document_id=...)` |
| `pop` | Retrieve **and remove/consume** an item from a store — mirrors `dict.pop`/`list.pop`. | either | `SessionStorePort.pop(session_id=...)` |
| `parse` | Convert free-form/loosely-structured text into a typed value, validating shape. | sync | `parse_money`, `_parse_amount` |
| `coerce` | Normalize an already-decoded, loosely-typed scalar (from JSON) into its precise domain type, inside a validator boundary. | sync | `coerce_confidence`, `coerce_to_bool` |
| `extract` | Derive a smaller, specific value out of a larger document/blob (may call a model/OCR). | either | `EntityExtractorPort.extract`, `extract_text_from_boxes` |
| `resolve` | Pick/derive the one definitive value among several candidate sources or branches. | sync | `_resolve_runtime_environment`, `_resolve_path` |
| `build` | Assemble a new composite object/message from already-known parts. | sync | `_build_messages`, `build_success_response` |
| `process` | The top-level orchestration entry point for a pipeline step/handler. | async | `Handler.process`, `process_json_request` |
| `from_dict` / `to_dict` | The canonical dict-shaped serialization-boundary pair (see `/` rule above). | sync | `Page.from_dict`, `Report.to_dict` |

Reserved but currently unused in this codebase — pick these only when the row
above genuinely does not fit, never as a synonym for one that does:

- `decode` — bytes → str character-set transcoding only, never a stand-in for `parse`.
- `deserialize` — a non-dict wire format (raw bytes, protobuf) where `from_dict`
  does not apply; if the source is already a `dict`/`JSONDict`, use `from_dict`.
- `analyze` — pairs with an `*Analysis` return DTO (mirrors `HandlerAnalysis`);
  do not add a bare `analyze()` without a matching `*Analysis` type.
- `convert` / `normalize` — avoid as a name; rename to `parse`, `coerce`,
  `resolve`, or a `to_*`/`from_*` pair so the direction and types are explicit.
