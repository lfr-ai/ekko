---
paths:
  - "**/*.py"
---

# Cognitive Load Instructions

Write code for human brains, not machines. Working memory holds ~4 chunks
simultaneously — every design decision is evaluated against that constraint.
Cognitive load splits into **intrinsic** (inherent to the problem domain,
managed only through good abstractions) and **extraneous** (caused by how code
is written/organized) — eliminate extraneous load ruthlessly; that is where all
improvement lives.

## Principles

1. **Deep modules over shallow** — prefer powerful functionality behind a
   simple interface (a class with 3 public methods encapsulating 200 lines of
   complex logic) over many shallow wrappers (10 tiny 20-line classes that must
   be understood together). Red flags: a method as complex as its interface, a
   wrapper adding no real abstraction, a name longer than its implementation,
   needing to read a callee to understand its caller. A 40-line method that
   reads top-to-bottom beats 8 five-line methods read together.
2. **Locality of behavior** — keep related code together; understanding a
   block should not require flipping between files. If two pieces are tightly
   related (entangled), bring them together rather than splitting them across
   adjacent methods.
3. **Extract complex conditionals** — name intermediate booleans that describe
   business meaning, not implementation details:

   ```python
   # High cognitive load
   if (
       order.amount > 10000
       and order.type == "digital"
       and not order.is_prepaid
       and days_since_submission > 30
   ):
       escalate(order)

   # Low cognitive load — each chunk has a clear name
   is_high_value = order.amount > 10000
   is_digital = order.type == "digital"
   needs_approval = not order.is_prepaid
   is_overdue = days_since_submission > 30
   if is_high_value and is_digital and needs_approval and is_overdue:
       escalate(order)
   ```
4. **Early returns over nesting** — each nesting level adds a chunk to working
   memory; early returns let the reader discharge conditions after passing them:

   ```python
   def process(order: Order) -> Result:
       if not order.is_valid:
           return Error("invalid")
       if order.amount <= 0:
           return Error("zero amount")
       if order.assignee is None:
           return Error("no assignee")
       return do_work(order)
   ```
5. **Balanced DRY** — a little duplication beats a wrong abstraction. Only
   extract when the duplication is genuine (same concept, same reason to
   change); never build a "generic helper" used in exactly one place, and never
   add a parameter count to a helper that exceeds the lines it replaces.
6. **Composition over deep inheritance** — inheritance beyond 2 levels forces
   readers to hold an entire hierarchy in mind; prefer a class that *uses* a
   `Validator`/`Calculator` over a 4-level subclass chain.
7. **Self-descriptive values** — use enums and named constants over magic
   numbers/strings that require memorization (`OrderStatus.APPROVED`, not `3`).
   Apply the same standard to names: short names in small scopes, descriptive
   names in large scopes; a megasyllabic name is harder to parse than the code
   it replaces.
8. **Comments explain WHY, not WHAT** — code already shows what it does through
   structure and naming; a comment earns its place only for intent, constraints,
   or a non-obvious decision (`# Upstream API requires this field even though
   the schema marks it optional`), never `# Increment counter`.

## Red Flags

- A method whose name is longer than its implementation.
- Needing to read a callee's code to understand the caller.
- "Flipping back and forth" between methods to trace flow.
- A helper requiring more parameters than the code it replaces.
- An abstraction that forces unrelated code to change together.

## Validation

Before completing code changes, verify:

- No function requires holding more than ~4 concepts in working memory.
- Complex conditionals are extracted into named intermediates.
- Nesting depth ≤ 2 levels (use early returns).
- No shallow methods that merely delegate without simplifying.
- Related code lives together (no entanglement across files).
- Comments explain WHY, not WHAT.
