---
description: Cognitive load management for writing human-readable code
applyTo: "**/*.py"
---

# Cognitive Load Instructions

Write code for human brains, not machines. The human working memory holds
approximately **4 chunks** simultaneously. Every design decision must be
evaluated against this fundamental constraint.

## Core Principle

> "The fundamental goal of software design is to make it easy to understand
> and modify the system." — John Ousterhout

Cognitive load is the total mental effort required to understand a piece of code.
Minimize it relentlessly.

## Types of Cognitive Load

| Type | Definition | Action |
|------|-----------|--------|
| **Intrinsic** | Inherent difficulty of the problem domain | Cannot be eliminated — only managed through good abstractions |
| **Extraneous** | Caused by how code is written/organized | **Eliminate ruthlessly** — this is where all improvement lives |

Focus all effort on reducing extraneous cognitive load.

## Deep Modules Over Shallow Modules

Prefer modules that provide **powerful functionality behind a simple interface**.
A deep module replaces a large cognitive load (reading the implementation) with
a much smaller cognitive load (learning the interface).

**DO:**
- A class with 3 public methods that encapsulates 200 lines of complex logic

**AVOID:**
- 10 tiny classes of 20 lines each that must be understood together
- Methods that are "entangled" — understanding one requires reading another

### Red Flags for Shallow Modules

- Extracting a method that has the same complexity as its interface
- Creating a wrapper that adds no real abstraction
- A function whose name is longer than its implementation
- Needing to read a callee's implementation to understand the caller

## Locality of Behavior

Keep related code together. If understanding a piece of code requires context
scattered across many files, the cognitive load multiplies.

**DO:**
- All information needed to understand a block is visible in that block
- Related operations live in the same module/class

**AVOID:**
- Splitting tightly-coupled logic across multiple tiny methods
- "Flipping back and forth" between implementations to understand flow

### Entanglement Rule

If two pieces of code are tightly related, bring them together. Separating
entangled pieces — even into adjacent methods — makes code harder to understand
because the reader must mentally reconstruct the whole.

## Extract Complex Conditionals

When conditionals require mental effort to parse, extract them into named
intermediate variables that describe the **business meaning**.

```python
# High cognitive load — reader must parse the entire expression
if (order.amount > 10000 and order.type == "digital"
    and not order.is_prepaid and days_since_submission > 30):
    escalate(order)

# Low cognitive load — each chunk has a clear name
is_high_value = order.amount > 10000
is_digital = order.type == "digital"
needs_approval = not order.is_prepaid
is_overdue = days_since_submission > 30

if is_high_value and is_digital and needs_approval and is_overdue:
    escalate(order)
```

## Prefer Early Returns

Reduce nesting depth. Each level of nesting adds one chunk to working memory.
Early returns allow the reader to discharge conditions from memory.

```python
# Nested logic — reader holds all conditions simultaneously
def process(order: Order) -> Result:
    if order.is_valid:
        if order.amount > 0:
            if order.assignee is not None:
                return do_work(order)
            else:
                return Error("no assignee")
        else:
            return Error("zero amount")
    else:
        return Error("invalid")

# Flat logic — reader can forget each guard after passing it
def process(order: Order) -> Result:
    if not order.is_valid:
        return Error("invalid")
    if order.amount <= 0:
        return Error("zero amount")
    if order.assignee is None:
        return Error("no assignee")
    return do_work(order)
```

## Balanced DRY — Don't Over-Abstract

A little duplication is far better than a wrong abstraction. Only extract shared
code when the duplication is **genuine** (same concept, same reason to change).

**DO:**
- Two methods share identical validation logic → extract

**AVOID:**
- Two methods have similar-looking code but represent different concepts → keep separate
- Creating a "generic helper" used in exactly one place

### Over-Abstraction Red Flags

- A helper that requires more parameters than the duplicated lines it replaces
- An abstraction that forces unrelated code to change together
- A shared utility that requires callers to understand its internals

## Composition Over Deep Inheritance

Inheritance depth beyond 2 levels forces readers to hold an entire class
hierarchy in memory. Prefer composition and protocols.

**DO:** `class OrderProcessor` that **uses** a `Validator` and `Calculator`

**AVOID:** `OrderProcessor → BaseProcessor → AbstractHandler → Mixable`

## Self-Descriptive Values

Avoid custom mappings that require memorization. Use enums, named constants,
and self-evident identifiers over magic strings and arbitrary codes.

```python
# Reader must memorize what "3" means
if status == 3:
    ...

# Self-describing
if status == OrderStatus.APPROVED:
    ...
```

## Comments for WHY, Not WHAT

Code should explain **what** it does through its structure and naming.
Comments should explain **why** — the intent, constraints, or non-obvious
decisions that the code cannot express.

**Good (WHY):**
- `# Skip division: multiplication is O(1) on this hardware`
- `# Upstream API requires this field even though the schema marks it optional`

**Bad (WHAT):**
- `# Increment counter` (the code already says this)
- `# Loop through items` (the for-loop is self-evident)

## Function and Method Length

There is no magic line count. The right size is determined by:

1. **Cohesion**: Does the method do one logical thing at the appropriate
   abstraction level?
2. **Independence**: Can it be understood without reading its callees?
3. **Interface simplicity**: Is the method signature simpler than the
   implementation it hides?

A 40-line method that reads top-to-bottom is better than 8 five-line methods
that must be read together.

## Naming as Cognitive Shortcut

Good names eliminate the need to read implementations.
Bad names create false confidence or force verification.

**DO:**
- Names that match the abstraction level of the context
- Short names in small scopes, descriptive names in large scopes

**AVOID:**
- Megasyllabic names that are harder to parse than the code they replace
- Names that imply no side-effects when side-effects exist

## Layer APIs at Multiple Complexity Levels

When designing modules, expose functionality at different levels:

1. **Simple API**: Common use cases with minimal parameters
2. **Power API**: Advanced use cases with full configuration

This lets most callers use the simple interface (low cognitive load) while
experts can access the full capability when needed.

## Complexity is in the Eye of the Reader

If a reader finds code hard to understand, the code **is** hard to understand.
"Familiarity is not simplicity" — code that seems clear to the author may be
opaque to others.

Test readability by asking: "Would a competent developer unfamiliar with this
specific module understand it without asking questions?"

## Summary Checklist

Before completing any code change, verify:

- [ ] No function requires holding more than ~4 concepts in working memory
- [ ] Complex conditionals are extracted into named intermediates
- [ ] Nesting depth ≤ 2 levels (use early returns)
- [ ] No shallow methods that merely delegate without simplifying
- [ ] Related code lives together (locality of behavior)
- [ ] Abstractions justify their existence (deep, not shallow)
- [ ] Comments explain WHY, not WHAT
- [ ] Names are self-descriptive at their abstraction level
