---
name: sdd
description: >
  Specification-Driven Development. Covers Given-When-Then scenario
  authoring, executable specs, living documentation, and the spec-first workflow.
  Integrated with OpenSpec for artifact-guided changes.
paths:
  - "docs/specs/**/*.md"
  - "openspec/specs/**/*.md"
  - "openspec/changes/**/specs/**/*.md"
---

# Skill: Specification-Driven Development (SDD)

**Specification by Example**: concrete, executable scenarios written before
implementation. A spec is simultaneously requirements documentation,
automated test, and living documentation — they are the same artifact.

## OpenSpec Integration

This project uses **OpenSpec** (`openspec/`) as the canonical spec management
framework. The source of truth lives in `openspec/specs/` organized by bounded
context. Changes are proposed via `openspec/changes/` with delta specs.

### OpenSpec Workflow Commands

| Command | Purpose |
|---------|---------|
| `/opsx:propose <name>` | Create a change with all planning artifacts |
| `/opsx:explore` | Investigate ideas before committing |
| `/opsx:apply` | Implement tasks from a change |
| `/opsx:verify` | Validate implementation matches specs |
| `/opsx:sync` | Merge delta specs into main specs |
| `/opsx:archive` | Finalize a completed change |

### Delta Spec Format (for changes)

```markdown
# Delta for <domain>

## ADDED Requirements

### Requirement: New Behavior
The system SHALL ...

#### Scenario: ...
- GIVEN ...
- WHEN ...
- THEN ...

## MODIFIED Requirements

### Requirement: Changed Behavior
(Previously: old behavior description)

## REMOVED Requirements

### Requirement: Deprecated Behavior
(Reason for removal)
```

### CLI Validation

```bash
openspec validate --all          # Validate all specs and changes
openspec list --specs            # List all domain specs
openspec status --change <name>  # Check artifact progress
```

## Core Principle

> "The spec is the test. The test is the spec."

Every significant behavior must have a spec scenario that:

1. Describes behavior in business language (Given-When-Then)
2. Maps directly to a passing automated test
3. Lives in `openspec/specs/` and stays in sync with code

## Spec Directory Structure

```text
openspec/specs/
├── context-a/
│   └── spec.md
├── context-b/
│   └── spec.md
├── context-c/
│   └── spec.md
├── context-d/
│   └── spec.md
├── api/
│   └── spec.md
└── persistence/
    └── spec.md
```

## Scenario Format (Given-When-Then)

OpenSpec uses a slightly different markdown structure from the older docs/specs
format. Both are supported:

**OpenSpec format** (preferred for `openspec/specs/`):
```markdown
#### Scenario: Valid order with available inventory is fulfilled

- GIVEN an order with product "WIDGET-001" and quantity 5
- AND inventory has 10 units of "WIDGET-001" available
- WHEN the fulfillment service processes the order
- THEN the order status is "FULFILLED"
- AND inventory for "WIDGET-001" is reduced to 5
```

**Legacy format** (for `docs/specs/`):
```markdown
## Scenario: Valid order with available inventory is fulfilled

**Given** an order with product "WIDGET-001" and quantity 5
**And** inventory has 10 units of "WIDGET-001" available
**When** the fulfillment service processes the order
**Then** the order status is "FULFILLED"
**And** inventory for "WIDGET-001" is reduced to 5
```

## Spec-First Workflow

### Step 1: Write the Spec
Create or update file in `openspec/specs/{domain}/spec.md`.
Use concrete examples and domain language.
For changes, use `/opsx:propose` to scaffold delta specs.

### Step 2: Turn Scenarios into Failing Tests
Map each scenario to a pytest test with scenario text in docstring.

```python
@pytest.mark.integration
async def test_valid_order_fulfilled(
    fulfillment_service,
    order_factory,
    inventory_factory,
) -> None:
    """Spec: order-processing/fulfillment.md
    Scenario: Valid order with available inventory is fulfilled.
    """
    # Given
    order = order_factory(product="WIDGET-001", quantity=5)
    inventory_factory(product="WIDGET-001", available=10)

    # When
    result = await fulfillment_service.process(order)

    # Then
    assert result.status == "FULFILLED"
    assert result.inventory_remaining == 5
```

### Step 3: Implement
Write the minimal code to make the spec/test pass.

### Step 4: Refine
Review spec language with stakeholders. Update if needed.

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
# Bad
Given the service calls the external API with retry=3

# Good
Given an order with product WIDGET-001 and available inventory
```

## Sync Policy

When behavior changes:
1. Update the spec scenario first
2. Update the test to match
3. Update the implementation
4. All three change in the same commit

## Checklist

- [ ] Every scenario has concrete input values
- [ ] Every scenario has concrete expected outcomes
- [ ] No implementation details in spec language
- [ ] Corresponding test cites spec file and scenario name
- [ ] Spec and test are in sync
