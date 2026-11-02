---
name: subagent-driven-development
description: Use when executing a multi-task implementation plan with independent tasks and fresh subagent implementation plus review cycles.
---

# Subagent-driven development

Use one bounded implementer per independent task, review the result with a fresh
read-only reviewer, and run a final integrated quality gate. Source-control
operations remain manual for the user; agents do not run version-control
commands.

## When to use

- An OpenSpec task list or approved plan has mostly independent work items.
- Each item can be completed with a self-contained brief and focused checks.
- For tightly coupled tasks or tasks requiring frequent user decisions, work
  inline instead.

## Prepare

1. Read the approved plan, relevant specs, repository policy, and local patterns.
2. Create or resume a task ledger in a task-specific ignored workspace directory.
   Record each task's brief, report path, acceptance criteria, and dependencies.
3. Confirm the user has selected an appropriate isolated workspace when the work
   could conflict with concurrent changes. Do not inspect or change branches.
4. Dispatch tasks in dependency order. Never run editing workers concurrently on
   overlapping files.

## Task cycle

1. Give a fresh implementer only the task brief, relevant interfaces, constraints,
   and expected report path. Require `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`,
   or `BLOCKED` plus changed paths, decisions, and focused verification evidence.
2. Resolve missing context or concerns before accepting the task. Do not silently
   broaden scope or discard a blocked task.
3. Ask a fresh read-only reviewer to inspect the named changed files against the
   brief and report correctness, missing tests, architecture/convention risks,
   and evidence. Do not use source-control commands or generated diff packages.
4. Fix every confirmed critical or important finding, then request a focused
   re-review. After five rounds, stop and report the remaining issue and rationale.
5. Record task completion, test evidence, and any explicit adjudication in the
   ledger before starting the next item.

## Model selection

Use the least capable available model that can handle the role. Prefer small
models for mechanical implementation and focused review; reserve stronger models
for architecture decisions and final integration.

## Final integration

After all tasks are reviewed, inspect the named files together for interface and
scope consistency, run the repository-declared quality gate, and reconcile docs
and specs. Report unverified checks and user-owned source-control actions; never
create branches, commits, or merges.
