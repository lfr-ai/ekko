---
description: Specification-Driven Development rules for OpenSpec scenario files
paths:
  - "openspec/specs/**/*.md"
  - "openspec/changes/**/specs/**/*.md"
---

# SDD Rules

## Core Rule

Every scenario in `docs/specs/` or `openspec/` specs must have a corresponding
passing automated test. A spec without a test is documentation rot.

## Scenario Format

Given-When-Then with concrete values:

```markdown
## Scenario: Valid order with available inventory is fulfilled

**Given** an order with product "WIDGET-001" and quantity 5
**And** inventory has 10 units available
**When** the fulfillment service processes the order
**Then** the order status is "FULFILLED"
**And** inventory is reduced to 5
```

## Prohibited in Specs

- Vague inputs: "some data", "a valid request"
- Implementation details: "calls API with retry=3"
- Vague outcomes: "an error is returned" (use the exact status code/exception)

## Test Link

Every implementing test cites the spec in its docstring:

```python
async def test_valid_order_fulfilled(...) -> None:
    """Spec: order-processing/fulfillment.md
    Scenario: Valid order with available inventory is fulfilled.
    """
```

## Sync Policy

When behavior changes: update spec → update test → update implementation.
All three change in the same commit.
