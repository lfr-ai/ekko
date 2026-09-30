---
name: "Align Consistency"
description: "Analyze the whole repository, then align it to one uniform voice — matching terminology/wording, filesystem & symbol naming, structural parallelism, documentation style, and cross-runtime agentic-setup parity — across code, tests, docs, specs, env templates, and the .github/.claude/.agents trees. Behavior-preserving, gate-verified, exhaustive, plan-driven."
category: "Conventions"
tags: ["consistency", "naming", "terminology", "structure", "documentation", "agentic-parity", "quality"]
---

Align the entire repository to a single, uniform voice — matching terminology,
naming, structure, and cross-runtime parity — so nothing looks bolted on. This is
the **horizontal uniformity** sweep: it checks that everything *matches its
siblings*, not that each file obeys the code rules in isolation.

**Companion prompts (compose, don't overlap):** per-file source code-rule
compliance is `align-conventions`; test-suite alignment is `align-tests`; the
three-tree agentic-setup mechanics are the `agent-config` skill and its guard.
This prompt owns cross-cutting *uniformity* and delegates those specifics to them.

**Scope (optional):** If a scope is given (a tree — `src/`, `tests/`, `docs/`,
`openspec/`, or the agentic trees `.github`/`.claude`/`.agents` — or a single
concept/term), restrict the walkthrough to it. Otherwise cover the whole repo:
the source package (named in `PROJECT.md`), `tests/`, `scripts/`, `sql/`,
`data/`, `alembic/`, `docs/`, `openspec/`, `docs/env-templates/`, the three
agentic trees, and the policy files (`AGENTS.md`, `CLAUDE.md`, `PROJECT.md`,
`llms.txt`).

## Non-negotiable constraints

1. **The canonical sources are the spec.** In order: `AGENTS.md` (Hard Rules),
   `PROJECT.md` (project facts + ubiquitous language), the paired
   `.github/instructions/*.instructions.md` ↔ `.claude/rules/*`, then the skills
   (`consistency`, `documentation`, `agent-config`, `clean-architecture`,
   `markdown`). When rules disagree, `AGENTS.md` wins.
2. **Behavior-preserving.** Renames, moves, and re-wordings must NOT change
   runtime behavior, public contracts, wire/DB names, or test outcomes. If a
   terminology fix would touch a public API path, an on-the-wire field, a
   database column, or an env-var name, do NOT force it — record it under
   "Behavioral risks (out of scope)".
3. **One concept, one home (refactor-first).** Never resolve an inconsistency by
   duplicating guidance. Pick the canonical wording/location, point every other
   mention at it with a link, and delete the duplicate. This applies doubly when
   aligning the agentic trees — extend or cross-link, never restate.
4. **Toolchain: uv + Task only.** Use `task` and `uv run`. Never `pdm`, `poetry`,
   `pipenv`, `conda`, `pip`, or bare `python`/`pytest`.
5. **No `git` commands.** All version-control actions are the user's.
6. **Enforce in place; do not add abstractions.** No new wrappers, shims, or
   synonym aliases "for compatibility". Removing a synonym, a stray duplicate, or
   a drifted copy IS in scope.

## Phase 1 — Inventory the repository's voice

- **Ubiquitous language.** Extract the domain nouns from `PROJECT.md`'s
  "Ubiquitous language" section. `grep_search` for near-synonyms and drift — any
  near-synonym used where an established domain term is meant.
- **Filesystem & symbol naming.** Establish the baseline with the two consistency
  guard scripts (Phase 6). Note every file whose name does not match its single
  public export, and every folder named for a category rather than a concept.
- **Structure.** Map sibling folders per layer and per agentic tree; flag any
  sibling whose shape diverges from the one it most resembles.
- **Agentic trees.** List skills, instruction↔rule pairs, agents, prompt↔command
  façades, hooks, and MCP names across `.github`/`.claude`/`.agents`; note any
  copy that has drifted from its mirror.
- Use `semantic_search`, `grep_search`, and `file_search` for discovery. Before
  renaming or moving any exported symbol, run `gitnexus_impact` to assess blast
  radius — a mandatory GitNexus Hard Requirement in `AGENTS.md`, not optional.

## Phase 2 — Consistency dimensions (align each)

Catalog every divergence, grouped by dimension:

- **Terminology & wording** — one term per concept everywhere (code, tests, docs,
  specs, comments, commit-message scopes, `memories/`); never a synonym for an
  existing concept. Match `PROJECT.md`'s ubiquitous language exactly; let `cspell`
  (`cspell.json`) own spelling.
- **Filesystem & symbol naming** — Python `snake_case.py` packages/modules,
  frontend `kebab-case.ts(x)`; folders named for the concept they hold; one
  primary public export per file with filename ↔ symbol correspondence;
  layer-role suffixes (`Port`/`Client`/`Repository`/`Store`/`Settings`/`Config`/
  `Handler`/`Orchestrator`/`Service`/`Manager`); acronyms fully upper. Rules and
  worked examples live in the `consistency` skill and `align-conventions`.
- **Structural parallelism** — a new or edited folder mirrors the sibling it most
  resembles (file layout, `__init__.py` role, test co-location); code sits in the
  layer matching its role; folders stay shallow; the inward dependency rule holds.
- **Documentation uniformity** — README/`docs/`/CHANGELOG follow the
  `documentation` skill and `markdown` instruction: consistent heading depth,
  fenced-code languages, link style (relative Markdown paths), table shape, and
  Keep-a-Changelog grouping. Link instead of duplicating.
- **Agentic three-tree parity** — skills byte-identical across `.github/skills`,
  `.claude/skills`, `.agents/skills`; every instruction pairs a `.claude/rules`
  file of equal scope (`applyTo` ↔ `paths`); agents paired across
  `.github/agents` ↔ `.claude/agents` (the Claude copy sets
  `user-invocable: false`); prompt ↔ command façades in bijection; hooks mirrored
  across `.github/hooks/*.json` and `.claude/settings.json`; MCP server names
  identical across `.mcp.json`/`.vscode/mcp.json`/`.claude/mcp.json`; every
  capability categorized in `.agents/agentic-setup/profiles.json`; every
  `llms.txt` link valid. Mechanics live in the `agent-config` skill.
- **Config & pattern uniformity** — env templates parallel across
  `docs/env-templates/*` (same keys, same order, per-environment values only);
  `Taskfile.yml` target naming; pre-commit hook ids; frontmatter shape consistent
  within each file class (prompts, commands, skills, instructions, rules, agents).

## Phase 3 — Research (web + documentation)

- Use Context7 (`mcp_context7_*`) and the web for version-accurate format specs
  when a dimension touches an external standard: Keep a Changelog, Conventional
  Commits, OpenAPI, the Agent Skills / `AGENTS.md` standard, and the VS Code
  prompt-file / instruction / skill schema. Cite sources in the plan.
- When aligning prompts, note the platform trajectory: VS Code prompt files are
  deprecated for Agent Host (migration target is Agent Skills), so keep durable
  guidance in the auto-discovered skill and the prompt as a thin orchestrator.

## Phase 4 — Extensive TODO / PLAN

Write a checkable plan BEFORE editing, grouped by tree then dimension. For each
item note the divergence found, the canonical form chosen, the fix, and the risk.
Keep "Behavioral risks (out of scope)" separate. Maintain it as a living
checklist and tick items off.

## Phase 5 — Systematic walkthrough (execute)

- Use `gitnexus_rename` (never find/replace) for every symbol rename — it
  understands the call graph across mirrored trees; update every call site,
  `__all__`, docstring, doc, and spec in the same change-set.
- For a per-file code-rule deviation surfaced en route, invoke `align-conventions`;
  for test drift, `align-tests`; for skill-mirror parity, follow `agent-config`
  and run `uv run .agents/skills/agent-config/scripts/sync.py --apply`.
- After renaming, moving, or adding a module or folder, refresh the code graph
  (`task graph`) so code intelligence stays accurate for the next pass.
- After each tree or logical group, re-check just what changed before moving on.

## Phase 6 — Full validation (iterate until clean)

- **Filesystem/class naming:**
  `uv run python .agents/skills/consistency/scripts/check_naming.py` and
  `uv run python .agents/skills/consistency/scripts/check_class_file_naming.py`.
- **Code & tests:** `task lint`, `task typecheck`, `task test`.
- **Agentic parity:** `uv run python .agents/guard/verify_agent_config.py`
  (skill/agent/prompt/command/hook/MCP parity, scopes, profiles, portability).
- **Specs:** `openspec validate --all` when specs changed.
- **Everything:** `task check` (pre-commit + `task guard`), then
  `gitnexus_detect_changes()` to confirm only the intended symbols and execution
  flows changed — required before any task is considered closed.

Introduce NO new `ty`/`ruff` diagnostics; leave pre-existing, unrelated baseline
items untouched and report them explicitly.

## Definition of done

- One term per concept repo-wide; no synonyms for an existing concept; the
  ubiquitous language is used exactly in code, tests, docs, and specs.
- Filesystem naming, symbol ↔ filename correspondence, and structural parallelism
  are uniform; the two consistency scripts pass.
- The three agentic trees are in parity; the agent-config guard passes.
- Documentation is uniform per the `documentation` skill; no behavior changed.
- Validation gates green (or only pre-existing, unrelated baseline noise remains —
  reported explicitly). Zero `git` commands run.
- `gitnexus_detect_changes()` confirms no unexpected symbol or process impact.
- Any durable lesson or recurring gotcha this pass surfaced is recorded in
  `memories/` (decisions or lessons) before the task is reported done.

## Final report

End with a concise `tldr;`:

- Per-tree / per-dimension changes (divergence found → canonical form → fix).
- Behavioral risks found (out of scope) with location and the public name at risk.
- Any pre-existing baseline items left untouched, and why.
- Final validation output (consistency scripts, ruff, ty, guard, test counts).
