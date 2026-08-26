---
description: Specification-Driven Development — scenario authoring rules
applyTo: "openspec/specs/**/*.md, openspec/changes/**/specs/**/*.md"
---

# SDD Instructions

Apply these rules to all spec files in `docs/specs/` and `openspec/specs/`.

## OpenSpec Integration

This project uses [OpenSpec](https://github.com/Fission-AI/OpenSpec) for
spec-driven development. The source of truth for system behavior lives in
`openspec/specs/` organized by bounded context:

Use OpenSpec slash commands to manage specs:
- `/opsx:propose` — Start a new change with artifacts
- `/opsx:apply` — Implement tasks from a change
- `/opsx:verify` — Validate implementation matches specs
- `/opsx:archive` — Finalize and merge delta specs

## Core Rule

Every spec scenario must have a corresponding passing automated test.
A spec without a passing test is documentation rot.

## Scenario Structure

Use Given-When-Then with **concrete values**:

```markdown
## Scenario: Valid order with available inventory is fulfilled

**Given** an order with product "WIDGET-001" and quantity 5
**And** inventory has 10 units available
**When** the fulfillment service processes the order
**Then** the order status is "FULFILLED"
**And** inventory is reduced to 5
```

## Concrete Values Required

| Avoid | Use instead |
|-------|-------------|
| "some data" | "an order with product WIDGET-001" |
| "a valid request" | "a POST to /api/v1/orders with quantity=5" |
| "an error is returned" | "the response status is 422 Unprocessable Entity" |
| "the data is saved" | "a record exists in DB with status=FULFILLED" |

## No Implementation Details

Specs describe WHAT, not HOW:

```markdown
# Bad — describes implementation
Given the service calls the external API with retry=3

# Good — describes observable behavior
Given an order with product WIDGET-001 and available inventory
```

## Scenario Naming

Follow: `{Action} {context/input} {expected outcome}`

## File Organization

One feature file per domain concept. Keep files small (≤ 10 scenarios).
Organize under the correct domain directory.

## Spec → Test Link

Every test that implements a scenario must cite the spec in its docstring:

```python
async def test_valid_order_fulfilled(...) -> None:
    """Spec: order-processing/fulfillment.md
    Scenario: Valid order with available inventory is fulfilled.
    """
```

## Sync Policy

When behavior changes:

1. Update the spec scenario first.
2. Update the test to match.
3. Update the implementation.
4. All three committed together.
