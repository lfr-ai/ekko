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

## Extract Complex Conditionals

When conditionals require mental effort to parse, extract them into named
intermediate variables that describe the **business meaning**.

```python
# High cognitive load
if (claim.amount > 10000 and claim.type == "dental"
    and not claim.is_preapproved and days_since_submission > 30):
    escalate(claim)

# Low cognitive load
is_high_value = claim.amount > 10000
is_dental = claim.type == "dental"
needs_approval = not claim.is_preapproved
is_overdue = days_since_submission > 30

if is_high_value and is_dental and needs_approval and is_overdue:
    escalate(claim)
```

## Prefer Early Returns

Reduce nesting depth. Each level of nesting adds one chunk to working memory.

```python
# Flat logic — reader can forget each guard after passing it
def process(claim: Claim) -> Result:
    if not claim.is_valid:
        return Error("invalid")
    if claim.amount <= 0:
        return Error("zero amount")
    if claim.assignee is None:
        return Error("no assignee")
    return do_work(claim)
```

## Balanced DRY — Don't Over-Abstract

A little duplication is far better than a wrong abstraction. Only extract shared
code when the duplication is **genuine** (same concept, same reason to change).

## Composition Over Deep Inheritance

Inheritance depth beyond 2 levels forces readers to hold an entire class
hierarchy in memory. Prefer composition and protocols.

## Summary Checklist

- [ ] No function requires holding more than ~4 concepts in working memory
- [ ] Complex conditionals are extracted into named intermediates
- [ ] Nesting depth ≤ 2 levels (use early returns)
- [ ] No shallow methods that merely delegate without simplifying
- [ ] Related code lives together (locality of behavior)
- [ ] Abstractions justify their existence (deep, not shallow)
- [ ] Comments explain WHY, not WHAT
- [ ] Names are self-descriptive at their abstraction level
