---
name: openspec-guide
description: "Use when the user asks about OpenSpec itself — available commands, workflows, spec structure, domain organization, or workflow reference. Examples: \"What OpenSpec commands are available?\", \"How do I use OpenSpec?\", \"How do specs work?\""
---

# OpenSpec Guide

Quick reference for all OpenSpec commands, workflows, spec domains, and the
artifact-driven development flow in this project.

## Always Start Here

For any task involving spec-driven development, behavioral changes, or feature work:

1. **Check active changes**: `openspec list`
2. **Check spec domains**: `openspec list --specs`
3. **Match your task to a skill below** and follow that workflow
4. **Validate before completion**: `openspec validate --all`

## Skills

| Task                                              | Skill to read              |
| ------------------------------------------------- | -------------------------- |
| Quick end-to-end change (all artifacts at once)   | `openspec-propose`         |
| Think through ideas before committing             | `openspec-explore`         |
| Start a new change (step-by-step)                 | `openspec-new-change`      |
| Create next artifact in sequence                  | `openspec-continue-change` |
| Fast-forward all planning artifacts               | `openspec-ff-change`       |
| Implement tasks from a change                     | `openspec-apply-change`    |
| Merge delta specs into main specs                 | `openspec-sync-specs`      |
| Validate implementation matches specs             | `openspec-verify-change`   |
| Archive a completed change                        | `openspec-archive-change`  |
| Archive multiple changes at once                  | `openspec-bulk-archive-change` |
| Guided onboarding tutorial                        | `openspec-onboard`         |
| OpenSpec reference (this file)                    | `openspec-guide`           |

## Slash Commands (Claude Code)

| Command             | Purpose                                      |
| ------------------- | -------------------------------------------- |
| `/opsx:propose`     | Create change + all artifacts in one step    |
| `/opsx:explore`     | Investigate ideas before committing          |
| `/opsx:new`         | Start a new change scaffold                  |
| `/opsx:continue`    | Create next artifact in sequence             |
| `/opsx:ff`          | Fast-forward all planning artifacts          |
| `/opsx:apply`       | Implement tasks from the change              |
| `/opsx:sync`        | Merge delta specs into main specs            |
| `/opsx:verify`      | Validate implementation matches specs        |
| `/opsx:archive`     | Archive a completed change                   |
| `/opsx:bulk-archive`| Archive multiple changes                     |
| `/opsx:onboard`     | Guided onboarding tutorial                   |

## Spec Domains (Source of Truth)

```text
openspec/specs/
├── case-intake/spec.md           → Customer, Case, InsuranceCondition
├── document-processing/spec.md   → Document retrieval, OCR, PDF extraction
├── case-assessment/spec.md       → AI pipeline orchestration, handlers
├── fraud-detection/spec.md       → Temporal rules, prior illness, recurrence
├── api/spec.md                   → REST endpoints, rate limiting, errors
└── persistence/spec.md           → Audit trail, data integrity
```

## Artifact Flow

```text
proposal ──► specs ──► design ──► tasks ──► implement ──► verify ──► archive
   │            │          │         │                        │
  why         what        how      steps                   check
```

## Delta Spec Format (for changes)

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
(Previously: old description)

## REMOVED Requirements
### Requirement: Deprecated Behavior
(Reason)
```

## CLI Reference

| Command                              | Purpose                           |
| ------------------------------------ | --------------------------------- |
| `openspec list`                      | List active changes               |
| `openspec list --specs`              | List all spec domains             |
| `openspec show <name>`              | View change or spec details       |
| `openspec validate --all`            | Validate all specs and changes    |
| `openspec status --change <name>`    | Artifact progress for a change    |
| `openspec instructions <id> --change <name> --json` | Get artifact template |
| `openspec schemas`                   | List available workflow schemas   |

## Integration with GitNexus

When making changes that affect code structure:

1. **Before proposing**: Use `gitnexus_query` to understand affected flows
2. **During design**: Use `gitnexus_impact` to assess blast radius
3. **After implementation**: Use `gitnexus_detect_changes` to verify scope
4. **Before archiving**: Run `openspec validate --all` + quality gate

## Integration with Context7

When specs reference library/framework behavior:

1. Use `mcp_context7_resolve-library-id` to find the library
2. Use `mcp_context7_query-docs` for current API documentation
3. Reference authoritative docs in design.md for implementation guidance

## Clean Architecture Enforcement

Specs are organized by bounded context, not by layer. However, tasks in
`tasks.md` MUST be ordered by Clean Architecture layer:

1. **Core** — Domain entities, value objects, protocols
2. **Application** — Use cases, orchestrators, DTOs
3. **Infrastructure** — Adapters, repositories, clients
4. **Presentation** — Routes, controllers, serialization
5. **Tests** — Unit → Integration → Property (TDD: test first)
