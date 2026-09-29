# Agent Operating Policy

This file defines the default operating policy for AI coding agents working in
any repository that includes it. It is **platform-agnostic** — any agent runtime
(IDE extension, CLI tool, cloud service, etc.) must follow these rules.

## Scope

This file contains cross-cutting behavioral rules that apply regardless of which
platform, toolchain, or project structure an agent uses. It does not reference
or depend on any platform-specific configuration directory, project layout, or
technology stack.

## Default Working Method

Apply this to every task unless the user explicitly asks for a lighter touch:

**IMPORTANT!** You MUST be exhaustive and follow best practices. Consult, search,
and fetch the web and relevant documentation. Make an extensive TODO/plan, then
run a systematic walkthrough ensuring everything is addressed and considered —
clean, aligned, consistent, up to date, and working. Keep cognitive load
manageable and follow the existing structure, setup, and conventions. Enforce
Clean Architecture and ensure alignment and consistency throughout the codebase.

## Response Format

End every response with a short `tldr;` section, placed **last** so it is easy to
find. Keep it minimal and human-readable — only the most important information
(key files touched, changes made, and any next step) as a few tight bullets, with
no extra prose. Omit the `tldr;` only when the user explicitly requests otherwise.

## Hard Rules

1. **No `Any`** — never introduce `Any` in production type annotations. Use
   concrete types, protocols, unions, or `object` as fallback.
2. **No `cast`** — never introduce `typing.cast`/`cast(...)` in production code.
   Refactor types, constructors, or helper boundaries so types are correct without casts.
3. **No quoted forward references** — do not use string-literal type annotations
   (for example `"AppConfig"`). Use `from __future__ import annotations` when
   forward references are needed.
4. **Explicit dataclass intent** — use `kw_only=True` on dataclasses.
    - Immutable/value-like classes: `@dataclass(frozen=True, kw_only=True, slots=True)`.
    - Mutable classes: `kw_only=True` and `slots=True` when compatible.
5. **Internal constants untyped** — never add type annotations to internal
   (underscore-prefixed) constants. Public constants may use `Final[...]`.
6. **Typed docstrings** — docstrings that include `Args`, `Returns`, `Yields`, or
   `Raises` sections must include explicit types in each entry.
    - Never start a docstring summary line with "Return", "Returns", "Response",
      "Request", or "Payload". Use a descriptive noun-phrase or imperative verb.
      - Use triple-quoted docstrings (`"""..."""`) for all docstrings.
    - Property docstrings: simple noun-phrase one-liners, no `Returns:` section.
7. **No `-> None` on `__init__`** — the implicit `None` return is universally
   understood and the annotation adds noise.
8. **Dead code removal** — remove unused methods, constants, imports, and stale
   helpers in the same change-set.
9. **Architecture boundaries** — respect the project's layered architecture
   import rules. Dependencies always flow inward.
10. **No legacy compatibility layers** — update call sites and tests to canonical
   symbols in the same change-set. No shims, alias modules, or deprecated
   wrappers.
11. **No git commands by agents** — agents must never execute `git` shell
   commands. Branching, staging, commit, reset, and push are always manual user
   actions.
12. **Follow language conventions** — adhere to the coding conventions defined
    in the project's conventions documentation.
13. **Cognitive load management** — write code for human brains (~4 chunks of
    working memory). Prefer deep modules, locality of behavior, named
    conditionals, and early returns over nesting.
14. **Annotated-first metadata** — prefer `typing.Annotated` for framework
    metadata declarations. Use assignment form when `default`, `default_factory`,
    or `alias` semantics require constructor clarity.
15. **Logging import consistency** — for stdlib logging, use `import logging`
    and module-qualified symbols (e.g. `logging.LogRecord`,
   `logging.getLogger`, `logging.handlers.TimedRotatingFileHandler`); avoid
   `from logging import ...` and `from logging.handlers import ...`.
16. **Custom type tiers** — classify a domain value by fixed trigger: an
    enforceable boundary invariant -> validated value object (`MaxTokens`,
    `Confidence`); a recurring compound shape -> structural `type` alias; a core
    stand-in for an outer-layer enum value -> decoupling `type` alias
    (`ModelDeploymentName`, `StrategyName`); an opaque distinct identifier ->
    `NewType`; otherwise a bare primitive (a count in arithmetic, free text,
    validated by its container value object when applicable). Never add a scalar
    `type` alias for documentation only (e.g. `PromptContent = str`).
   Retrieval example: use `MaxTokens` for constrained budgets like
   `RetrievalQuery.max_context_tokens`; keep measured counters like
   `RetrievalDiagnostics.prompt_tokens` and `retrieved_chunks` as primitive
   `int` values. An internal knob whose only source is a validated module
   constant (e.g. `RAG_TOP_K: Final[int]`) does not cross a trust boundary and
   stays a bare primitive: `top_k`, `chunk_size`, and `chunk_overlap` are `int`,
   not value objects.
17. **First-party import intent** — import first-party symbols directly. A test
   or tool may import a first-party module object (for example
   `import myapp.main as main_module`) only for monkeypatching, reloading, or
   package-surface assertions; this is not permission to mix symbol styles.
18. **Boundary exceptions are narrow** — Core is stdlib-only except Pydantic
   schema dunder hooks in scalar/value-object modules. Infrastructure never
   imports Application. Presentation never imports the concrete Composition
   container and obtains request-state dependencies through structural protocols.
19. **One package manager** — use only the package manager declared by the
   repository (see its toolchain documentation). Never invoke a different one
   "just to run something": foreign package managers write stray state files
   (for example `.pdm-python`, `__pypackages__/`, `poetry.lock`) that pollute
   the working tree. If a command fails, fix the invocation with the declared
   tool — do not switch tools.
20. **Configuration facets & `from_config`** — name environment-sourced
   configuration facets `*Settings` (each owns one cohesive group of fields and
   composes into the app config) and complete assembled configurations `*Config`
   (the aggregate app config plus its per-environment subclasses). A component
   built from configuration exposes `from_config(cls, config: _XConfig)`, where
   `_XConfig` is a private structural `Protocol` (same module) of only the fields
   it reads; it never imports the concrete app config, which satisfies `_XConfig`
   structurally (PEP 544, dependency inversion). Name such a consumer view
   `_<Component>Config`, never `_<…>Settings`.

## Mandatory Execution Workflow

1. Scan the repository for policy compliance before and after edits.
2. Identify the declared package manager before running anything: check for a
   lockfile (`uv.lock`, `poetry.lock`, `pdm.lock`) and the corresponding
   `[tool.*]` table in `pyproject.toml`. Use that tool and no other.
3. Validate all configured checks before completion:
    - Run the project's test suite using its configured task runner.
    - Run linting and static analysis using the project's configured tools.
    - Run pre-commit hooks when configuration exists.
4. Do not close work while any required check is failing.

## Compliance Checklist

- Dead code removed in same change-set.
- Architecture boundaries respected.
- Language-specific conventions followed.
- Cognitive load minimized: no shallow wrappers, no scattered context, no deep
  nesting, conditionals are named.
- No `git` shell commands executed by agents.
- No foreign package-manager artifacts created (`.pdm-python`, `.pdm.toml`,
  `pdm.lock`, `poetry.lock`, `Pipfile*`, `__pypackages__/`).

## Agent Profiles

| Agent           | Use For                                                                  |
| --------------- | ------------------------------------------------------------------------ |
| `ddd`           | Domain-Driven Design, domain modeling, bounded contexts, aggregates      |
| `sdd`           | Specification-Driven Development, executable specs, living documentation |
| `tdd`           | Test-Driven Development, Red-Green-Refactor cycles, test suites          |
| `debug`         | Defect isolation, root cause analysis, systematic troubleshooting        |
| `deep-thinking` | Complex problem analysis, architectural trade-offs, strategic decisions  |
| `devops`        | Docker, CI/CD, infrastructure, deployment, containerization              |
| `modernization` | Large-scale analysis, documentation, migration planning                  |
| `refactor`      | Code refactoring, technical debt reduction, code smell elimination       |
| `testing`       | Test strategy, quality assurance, coverage analysis                      |

All agents use identical names and responsibilities across platforms. When a task
clearly matches a profile, apply that profile's workflow end-to-end.

## Agent Capability Baseline

All agents are **execution-capable by default**:

- Read and search codebase context.
- Edit and write files.
- Run terminal commands and scripts for build/test/validation (except `git`).
- Use configured tooling for code-graph intelligence and documentation lookup.

Do not restrict per-agent tools unless there is a documented security reason.

## Non-Negotiable Rules

1. **Run project-native tooling first** — use the repository's declared task
   runner and package manager only; never substitute another one
2. **Keep changes minimal**: One logical change per commit
3. **Update docs in same change**: When behavior or config changes
4. **Respect architecture boundaries**: No cross-layer violations
5. **Full repository audit**: Before and after changes
6. **Run validation gates**: Before completing work
7. **No legacy shims**: No backward-compatibility layers or deprecated code
8. **No secrets in code**: Use environment variables or secret management
9. **No git commands by agents**: All git operations are manual by the user

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **ekko** (4341 symbols, 6584 relationships, 82 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/ekko/context` | Codebase overview, check index freshness |
| `gitnexus://repo/ekko/clusters` | All functional areas |
| `gitnexus://repo/ekko/processes` | All execution flows |
| `gitnexus://repo/ekko/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/cli/SKILL.md` |

<!-- gitnexus:end -->
