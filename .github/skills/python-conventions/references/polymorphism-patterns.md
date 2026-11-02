# Polymorphism patterns

Loaded on demand from `python-conventions/SKILL.md` — read this only when
choosing how to model variation (multiple types/behaviors behind one call
site), reviewing an `isinstance`/type-tag chain, or adding a new port/adapter.

## Decision table

| Situation | Use | Why |
| --- | --- | --- |
| Adapters must satisfy a port (repository, client, store) | `Protocol` (structural) | No inheritance coupling; a `Fake*` test double satisfies it without subclassing (PEP 544) |
| Several implementations share real behavior, not just a signature | `ABC` + `@abstractmethod` | Only justified when there is common code to inherit — an interface alone stays `Protocol` |
| A closed, rarely-changing set of variants (an enum you own) | `match` statement or a `dict[Enum, Callable]` dispatch table | The type checker proves exhaustiveness; no new subclass wiring needed |
| Dispatch on a type you don't own (stdlib/third-party) and can't add a method to | `functools.singledispatch` / `singledispatchmethod` | Extends behavior for a foreign type without monkeypatching or wrapping |
| Ad hoc interop with a foreign/dynamic object at a single call site, no repeated shape | `hasattr`/`getattr` runtime duck typing | A `Protocol` adds no value for one call site with no second user (PEP 544 calls the typed form "static duck-typing" — reach for it once the shape repeats) |
| Only one implementation exists and no second is planned | A plain function or class — no abstraction | Speculative generality (YAGNI); add the seam when a second implementation is real |

## Nominal vs structural typing

Python supports both; this codebase uses each deliberately (PEP 544 keeps them
complementary — it does not replace nominal typing):

- **Structural** (`Protocol` — PEP 544 "static duck typing") — compatibility is
  by *shape*: any object with matching members qualifies, with no import or base
  class. The default for **ports**, so a `Fake*` double or a third-party object
  satisfies the contract without subclassing it.
- **Nominal** (explicit `class Adapter(Port)`, `ABC`, `Enum`) — compatibility is
  by *declared identity* in the MRO. Use it when you need `isinstance`, shared
  executable code (an `ABC` template method), or a closed identity a checker can
  reason about exhaustively.

Adapters take **both**: a structural `Protocol` port *and* an explicit nominal
base (`class ChatClient(ChatClientPort)`) so the checker verifies the
implementation and `@override` guards every method. Mark a port
`@runtime_checkable` only when a real `isinstance` gate needs it — it checks
member *presence*, not signatures, and `issubclass` works only for method-only
(non-data) protocols (PEP 544).

## Structural polymorphism via `Protocol` (default in this codebase)

Every port in `core/ports/` is a `Protocol`; every adapter subclasses its port
explicitly and decorates each method `@override` (mechanical Liskov
Substitution check — a widened exception or narrowed parameter fails type
checking). See the `ddd` skill's
[`assets/service_port_protocol.py.template`](../../ddd/assets/service_port_protocol.py.template) +
[`assets/service_adapter.py.template`](../../ddd/assets/service_adapter.py.template),
and `ddd`'s `scripts/check_port_adapter_binding.py`, which enforces both the
`Protocol` base and the `@override` decorator.

```python
class ChatClientPort(Protocol):
    async def complete(self, *, prompt: str) -> str: ...


class ChatClient(ChatClientPort):
    @override
    async def complete(self, *, prompt: str) -> str: ...
```

Prefer `Protocol` over `ABC` for ports: it needs no shared `__init__`, a test
double satisfies it structurally, and it does not force every adapter into one
inheritance tree. Reach for `ABC` only when adapters genuinely share
executable code (a template-method base), never merely to declare a shape.

## Replace Conditional with Polymorphism

An `isinstance`/type-tag `if`/`elif` chain that grows every time a new variant
is added is an Open/Closed violation (see the `solid-review` agent). Replace it
with a `Strategy` keyed by the tag, each strategy satisfying one `Protocol`:

```python
# Before: every new kind requires editing this function
def render(shape: object) -> str:
    if isinstance(shape, Circle):
        return f"circle r={shape.radius}"
    if isinstance(shape, Square):
        return f"square s={shape.side}"
    raise TypeError(f"Unsupported shape: {type(shape)!r}")


# After: adding Triangle only adds a class + a registry entry
class ShapeRendererPort(Protocol):
    def render(self) -> str: ...


class Circle(ShapeRendererPort):
    @override
    def render(self) -> str:
        return f"circle r={self.radius}"


class Square(ShapeRendererPort):
    @override
    def render(self) -> str:
        return f"square s={self.side}"


def render(shape: ShapeRendererPort) -> str:
    return shape.render()
```

Do not apply this refactor to a **closed** enum-driven set (see next
section) — a `match` on your own `StrEnum` is not the smell this fixes; the
smell is a chain that must be edited at multiple call sites every time a new
*type* appears.

## Closed variant sets: `match`/dispatch table over subclassing

When the set of variants is a `StrEnum`/`IntEnum` you own and rarely
changes, a `match` statement or a `dict[Enum, Callable]` is simpler than a
class per variant — `ty`/`ruff` cannot prove exhaustiveness across separate
classes, but a `match` over a closed enum is easy to read top-to-bottom:

```python
match strategy:
    case RagStrategy.LIGHT:
        return LightRetriever()
    case RagStrategy.DEEP:
        return DeepRetriever()
    case RagStrategy.GRAPH:
        return GraphRetriever()
```

## `functools.singledispatch` for foreign types

Use `singledispatch`/`singledispatchmethod` only when the variation is on a
type you cannot add a method to (stdlib types, third-party DTOs) — never as a
substitute for `Protocol` on your own ports:

```python
from functools import singledispatch


@singledispatch
def to_jsonable(value: object) -> object:
    raise TypeError(f"Unsupported type: {type(value)!r}")


@to_jsonable.register
def _(value: Decimal) -> str:
    return str(value)


@to_jsonable.register
def _(value: datetime) -> str:
    return value.isoformat()
```

## Anti-patterns

- **Speculative interface** — introducing a `Protocol`/`ABC`/Strategy for a
  single call site with no second implementation planned (see the
  `solid-review` agent's own anti-pattern list and the `ponytail`/minimalism
  skill). Add the abstraction when the second real implementation exists.
- **Inheritance for code reuse only** — subclassing purely to share a helper
  method with no "is-a"/substitutability relationship. Extract the helper
  into a module function or compose it instead.
- **`isinstance` chain that keeps growing** — a strong signal a `Protocol` +
  `@override` pair belongs here instead (see "Replace Conditional with
  Polymorphism" above).
- **Widening a subtype's contract** — an override that accepts a narrower
  input or raises a broader exception than its `Protocol`/`ABC` declares
  breaks Liskov Substitution even though `@override` alone cannot detect a
  narrowed *runtime* precondition — review call sites, not just signatures.

## `@final` / `@override` placement

Import both from `typing`, never `typing_extensions`. Order: `@final` directly
above `class`, `@override` directly above `def`.

| Symbol | Apply to | Skip on |
| --- | --- | --- |
| `@final` | Composed service classes (handlers, orchestrators, services, clients, repositories, stores, managers, configs, the container) and any method subclasses must not override | An `ABC`, `Protocol`, or extension base others deliberately subclass; data types; edge adapters; `_`-prefixed classes |
| `@override` | Every concrete override of a base/`ABC`/`Protocol` member the class explicitly subclasses | `__init__`/`__new__`/`__post_init__`; a new `@abstractmethod`; data types; edge adapters; `_`-prefixed classes |

`@final` seals a class against subclassing and a method against override;
`@override` is a mechanical Liskov check the type checker verifies against the
declared base. A class is often both (`@final` on the class, `@override` on the
port methods it implements). Never `@final` a type designed as an extension
point, and never `@override` a method whose base does not declare it.
