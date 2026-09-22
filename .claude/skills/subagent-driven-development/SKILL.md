---
name: subagent-driven-development
description: Use when executing a multi-task implementation plan (an OpenSpec tasks.md or an ad-hoc plan file) in the current session and want a fresh subagent per task with two-stage review. Use when a plan's tasks are mostly independent and you want fast iteration without a human checkpoint between every task.
---

# Subagent-Driven Development

Dispatch a fresh implementer subagent per task, review each task (spec
compliance + code quality), then run one broad review at the end. Adapted
from the open-source [Superpowers](https://github.com/obra/superpowers)
project's skill of the same name, with all git-branch/worktree ownership
removed: **Hard Rule 11** (`AGENTS.md`) forbids agents from running `git` —
branching, merging, and pushing stay manual, always.

**Core principle:** fresh subagent per task + task review (spec + quality) +
broad final review = high quality, fast iteration, without polluting your
own context with every task's implementation detail.

## When to use

- You have a plan with mostly-independent tasks (an OpenSpec change's
  `tasks.md`, or an ad-hoc plan you or the user wrote) and want to execute it
  in the current session.
- Tasks are tightly coupled or need constant human judgment calls → execute
  inline yourself instead; this skill adds overhead for no benefit there.
- The plan is an OpenSpec change with simple, small tasks → plain
  `opsx/apply-change` may already be enough; reach for this skill when you
  additionally want per-task subagent isolation and a two-stage review gate.

## Setup: no worktrees, no agent-owned branches

1. **Confirm isolation already exists.** Check the active branch (via the IDE
   Source Control view, not a `git` command). If it's `main`/`master`, stop
   and ask the user to create/check out a feature branch first — that is
   their manual action, not yours.
2. **Resolve this plan's workspace**: a git-ignored scratch directory at
   `.sdd/<plan-slug>/`, where `<plan-slug>` is the plan file's basename
   without extension. Every artifact for this plan lives there: ledger, task
   briefs, reports, review packages. Never read or write another plan's
   directory. Add `.sdd/` to `.gitignore` if not already present.
3. **Check for an existing ledger** at `.sdd/<plan-slug>/progress.md`. A
   `Task <N>: complete` line means that task is done — resume at the first
   task without one. A ledger naming a different plan file belongs to
   another plan; leave it alone.
4. **Create the ledger** if none exists, with its identity as the first
   line: `# SDD ledger — plan: <plan file path>`.
5. Read the plan once, create a todo per task. If it names a spec (an
   OpenSpec change's `proposal.md`/`design.md`, or a linked design doc), read
   that too — it is the binding authority; the plan is its argument.

## Model selection

Use the least capable model that can handle each role — conserves cost and
is usually faster (fewer retry turns), not just cheaper per-token.

| Task shape | Model tier |
| --- | --- |
| Mechanical, 1-2 files, spec fully in the brief (transcription + tests) | Cheapest available |
| Multi-file integration, pattern-matching, debugging | Standard |
| Architecture/design judgment, the final whole-plan review | Most capable available |
| Fix-loop rounds 4-5 (implementer got stuck twice already) | At least one tier above the stuck implementer |

Always specify the model explicitly when dispatching — an omitted model
inherits your own, usually the most expensive, silently defeating this table.

## The per-task loop

1. **Dispatch the implementer.** Extract the task's full text to
   `.sdd/<plan-slug>/task-<N>-brief.md` and give the subagent that path plus:
   where the task fits, interfaces from earlier tasks it needs, and the
   report-file path/contract (`.sdd/<plan-slug>/task-<N>-report.md`). Never
   paste the whole plan or prior tasks' history into the dispatch — a fresh
   subagent needs only its task and the interfaces it touches.
2. **Handle the report.** The implementer returns one of:
   - `DONE` → generate the review package (a diff summary of the task's
     changed files) and dispatch a reviewer.
   - `DONE_WITH_CONCERNS` → read the concerns; address correctness/scope
     doubts before review, note pure observations and proceed.
   - `NEEDS_CONTEXT` → provide the missing context, re-dispatch same model.
   - `BLOCKED` → assess: more context, a more capable model, split the task,
     or rule on a plan defect (ledger the ruling) and re-dispatch.
3. **Review the task.** Dispatch a fresh, unnamed subagent (or a relevant
   specialist agent, e.g. `refactor` for coupling/design concerns, `testing`
   for coverage gaps) with: the brief, the report, the changed-file list, and
   the plan's binding constraints copied verbatim. Require both a
   spec-compliance verdict and a code-quality verdict — neither replaces the
   other, and the implementer's self-review replaces neither.
4. **The fix loop.** Triggers on spec ❌, any Critical/Important finding, or a
   confirmed gap. Max 5 rounds per task, one fix + one scoped re-review each:
   - Rounds 1-3: resume the same implementer with the findings verbatim.
   - Rounds 4-5: fresh implementer, a more capable model (see Model
     Selection), framed as "a prior implementer tried this N times — read
     the report file for what was attempted."
   - After round 5, adjudicate yourself: park a wrong-or-contestable finding
     with a ruling, or — if it's real and load-bearing — rule on the
     smallest unblocking change and carry it into later tasks. Every
     adjudication is a ledger entry; a silent discard is forbidden.
5. **Complete the task.** Append `Task <N>: complete (review clean)` (or
   `, <K> parked` after a tripped breaker) to the ledger, mark the todo
   complete, move to the next task.

Batch several small same-shape edits (the same one-line fix repeated across
files) into a single dispatch instead of one subagent per file.

## Final review

When all tasks are complete, dispatch a whole-branch review (the full set of
changed files across every task) on the most capable available model. If it
returns findings, dispatch **one** fix subagent with the complete list (never
one fixer per finding), then one scoped re-review of that fix range.
Adjudicate any residual findings the same way as the per-task breaker.

## Finish — hand off, don't merge

This skill's job ends here — merging, pushing, and branching stay the user's
call (Hard Rule 11). When the final review is clean:

1. Collect every ledger line containing a ruling into your final message
   under "Rulings I made" — the only place those decisions reach the user.
2. Delete the scratch workspace (`.sdd/<plan-slug>/`) — the git history is
   the durable record now.
3. Report what changed, current branch state, and that merge/push/PR
   creation is the user's call — same as every other git operation in this
   repo.

## Common rationalizations

| Excuse | Reality |
| --- | --- |
| "I'll just merge it myself, saves a round trip" | Hard Rule 11. Never — report and stop. |
| "Close enough on spec compliance" | A spec gap is not done. Fix or hit the cap and adjudicate. |
| "One more fix round will converge" | Past the cap, rounds don't converge — the failure is structural. Adjudicate. |
| "I'll fix it myself instead of resuming the implementer" | That pollutes your own context and skips review. Resume or re-dispatch. |
| "Ledger bookkeeping is overhead" | It is what survives context compaction — the fastest failure mode is re-dispatching a completed task sequence. |

## Quick reference

| Situation | Action |
| --- | --- |
| On `main`/`master` | Stop, ask user to switch branches first |
| Ledger has `Task <N>: complete` | Skip it, resume at the next task |
| Ledger names a different plan | Leave it, start your own |
| Implementer reports `BLOCKED` | Assess cause, don't force a bare retry |
| Review returns Minor only | Ledger as deferred, never enters the fix loop |
| Fix loop round 5 still open | Adjudicate yourself, ledger every ruling |
| All tasks + final review clean | Delete workspace, report, hand off — no merge |
