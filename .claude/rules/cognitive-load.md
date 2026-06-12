---
paths:
  - "**/*.py"
---

# Cognitive Load

Write code for human brains. Working memory holds ~4 chunks simultaneously.

## Principles

1. **Deep modules over shallow** — simple interfaces hiding complex implementations.
   A 40-line method that reads top-to-bottom beats 8 five-line methods that must
   be understood together.

2. **Locality of behavior** — keep related code together. If understanding a piece
   of code requires context scattered across many files, cognitive load multiplies.

3. **Extract complex conditionals** — name intermediate boolean variables that
   describe business meaning, not implementation details.

4. **Early returns over nesting** — each nesting level adds a chunk to working
   memory. Flat code lets readers discharge conditions after passing them.

5. **Balanced DRY** — a little duplication is better than a wrong abstraction.
   Only extract when duplication represents the same concept with the same reason
   to change.

6. **Comments for WHY** — code shows WHAT; comments explain intent, constraints,
   and non-obvious decisions.
