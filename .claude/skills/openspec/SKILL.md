---
name: openspec
description: Spec-driven planning workflow for requirement-first feature design. Use when planning multi-step features, creating requirement specs before implementation, or coordinating cross-layer changes.
when_to_use: When a feature needs explicit requirements before coding, when coordinating multi-step implementation plans across layers, or when creating spec deltas for review before touching code.
---

# Skill: OpenSpec

Use this skill for requirement-first planning, especially when requested to create or
review specification deltas before code changes.

## When to use

- A feature requires explicit requirements and scenarios before implementation.
- You want a concise spec delta that reviewers can validate quickly.
- You are coordinating multi-step implementation plans across layers.

## Core workflow

1. Confirm OpenSpec CLI is available (`openspec --help` or npm global install).
2. Draft/update a focused spec for the change (requirements + scenarios).
3. Produce a spec delta and review it before coding.
4. Implement code in small increments that map directly to spec items.
5. Update tests and docs to match the finalized spec.

## Quality bar

- Specs should be concrete and testable.
- Every major behavior change should map to at least one scenario.
- Prefer iterative spec updates over one large monolithic spec change.
