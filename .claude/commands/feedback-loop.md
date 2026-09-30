---
name: "Feedback Loop"
description: "Run the repository's Deterministic Feedback Loop end-to-end for a non-trivial change — analyze, research, clarify, implement, validate against every gate, review, and update memory. Cost-aware and subagent-orchestrated; defers to AGENTS.md as canonical."
category: "Workflow"
tags: ["workflow", "feedback-loop", "quality", "clean-architecture", "validation", "memory"]
---

Execute the repository's **Deterministic Feedback Loop** for the task you were
given, end-to-end. The always-on baseline is `AGENTS.md`'s "Default Working
Method"; this prompt is its detailed, on-demand expansion — it *orchestrates*
that baseline, it does not redefine it. Read that section first and treat it as
the source of truth. Compose with the focused prompts instead of duplicating
them: `align-conventions` (convention/naming/clean-architecture sweep),
`align-consistency` (whole-repo terminology/structure/parity uniformity),
`align-tests` (test alignment), `commit-message` (final message).

## Operating rules

1. **Scale breadth to risk.** A local edit gets a focused slice; cross-cutting,
   data, security, or infrastructure work gets whole-system coverage. Do NOT
   rescan unrelated files to appear thorough — touch only what the task needs.
2. **Toolchain: uv + Task only.** Never `pdm`/`poetry`/`pipenv`/`conda`/`pip` or
   bare `python`/`pytest`.
3. **No `git` commands** — version control is the user's.
4. **External resources are read-only** — the tool guardian deterministically
   blocks database/Azure/infrastructure mutations; never work around it.

## Walkthrough (checkpoint each; stop early when the task is trivial)

1. **Orient** — load only the instructions, skills, and rules whose scope matches
   the task; read `PROJECT.md`, `memories/`, `.agents/knowledge-base/`, and the
   relevant specs and tests. Delegate broad read-only discovery to a parallel
   exploration subagent to preserve main-thread context.
2. **Analyze** — inventory the affected surface and its dependencies; use the
   code-graph tools (`gitnexus_impact`, `gitnexus_context`) before changing any
   symbol. State scope, risks, and acceptance criteria. Never infer behavior from
   folder names.
3. **Research** — when APIs, tools, versions, or security controls matter, verify
   against current documentation (Context7, Microsoft Learn, web) before coding;
   cite sources and separate verified facts from assumptions.
4. **Clarify** — ask only the questions whose answers change the design or safety;
   otherwise state the safe assumption and proceed.
5. **Implement** — small vertical increments; tests-first for defects and fragile
   mechanics; reuse existing abstractions; follow the conventions and
   DRY/KISS/YAGNI. Keep cognitive load low (deep modules, named conditionals,
   early returns).
6. **Validate** — run focused checks per increment, then every completion gate
   once after the final edit: `task test`; `uv run ruff format --check .` and
   `uv run ruff check .`; `uv run ty check src tests scripts`;
   `uv run pre-commit run --all-files`; and, when agent configuration changed,
   `uv run python .agents/guard/verify_agent_config.py`. Fix causal failures;
   never weaken a gate. Evidence must be fresh in the completion message.
7. **Review** — re-check requirements, behavior, architecture boundaries, naming
   (functions, variables, args, files, folders, classes, suffixes), folder
   ownership, cognitive load, security, and documentation. Run `align-conventions`,
   `align-consistency`, or `align-tests` for a dedicated sweep when the change is
   broad.
8. **Learn** — update `memories/` ONLY for a new verified fact, durable decision,
   recurring lesson, or unfinished handoff (one
   `memories/handoffs/YYYY-MM-DD-<task>-<agent>.md` per parallel agent). Refresh
   docs and env templates made stale by the change. Never store transcripts,
   secrets, or speculation.
9. **Repeat** — continue from the first failed or changed checkpoint until the
   implementation and fresh validation evidence agree.

End with a short `tldr;` (files touched, changes made, any next step).
