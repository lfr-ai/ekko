---
name: openspec
description: Use OpenSpec for spec-driven planning and change proposals before implementation.
---

# Skill: OpenSpec

Use this skill for requirement-first planning and behavior-driven change design
before code changes.

## When to use

- Multi-file or non-trivial feature work needs structured intent and scope.
- You want explicit requirement deltas and scenario-based validation.
- You are coordinating changes across backend/frontend/infra boundaries.
- You need an auditable change artifact trail (proposal/design/tasks/spec deltas).

## Core workflow

1. Confirm OpenSpec CLI is available (`openspec --help`).
2. Ensure OpenSpec project scaffolding exists (`openspec/` directory structure).
3. Start the change with `/opsx:propose <change>` (default) or
	`/opsx:new <change>` + `/opsx:continue`/`/opsx:ff` (expanded).
4. Keep specs behavior-first and use requirement deltas:
	- `## ADDED Requirements`
	- `## MODIFIED Requirements`
	- `## REMOVED Requirements`
5. Use `/opsx:apply` to implement tasks and keep artifacts updated as learning
	emerges.
6. Optionally verify with `/opsx:verify` (expanded profile).
7. Merge deltas with `/opsx:sync` and finalize with `/opsx:archive`.

## Artifact model

- `openspec/specs/` — source of truth for current behavior.
- `openspec/changes/<change>/proposal.md` — intent, scope, approach.
- `openspec/changes/<change>/specs/**/spec.md` — behavior deltas.
- `openspec/changes/<change>/design.md` — technical approach decisions.
- `openspec/changes/<change>/tasks.md` — implementation checklist.

Keep implementation details out of behavior specs.

## Quality bar

- Specs should be concrete and testable.
- Every major behavior change should map to at least one scenario.
- Prefer iterative updates over monolithic one-shot changes.
- Keep each change focused to one logical unit of work.
- Use clear, kebab-case change names.
- Ensure archive only after implementation and spec sync are coherent.
