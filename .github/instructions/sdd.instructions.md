---
description: Specification-Driven Development — scenario authoring rules
applyTo: "docs/specs/**/*.md, openspec/specs/**/*.md, openspec/changes/**/specs/**/*.md"
---

# SDD Instructions

Apply these rules to all spec files in `docs/specs/` and `openspec/specs/`.
Scenario format, OpenSpec workflow, and worked examples live in the `sdd`
skill (`.agents/skills/sdd/SKILL.md`) — pull it up for deep patterns.

## Core Rule

Every spec scenario must have a corresponding passing automated test.
A spec without a passing test is documentation rot.

## Rules

- Use Given-When-Then with concrete values ("product WIDGET-001", not
  "some data"); specs describe observable behavior (WHAT), never
  implementation details (HOW).
- Scenario naming: `{Action} {context/input} {expected outcome}`.
- One feature file per domain concept; keep files small (≤ 10 scenarios).
- Every test implementing a scenario cites the spec file and scenario name
  in its docstring.

## Sync Policy

When behavior changes: update the spec scenario first, then the test, then
the implementation — all three committed together.
