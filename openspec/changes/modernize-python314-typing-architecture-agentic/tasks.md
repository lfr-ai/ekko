# Tasks: modernize-python314-typing-architecture-agentic

## 1. Baseline and Inventory

- [x] 1.1 Record exact local versions for Python, uv, Ruff, ty, PyInstaller, Node, Bun, and container tooling.
- [x] 1.2 Inventory every active Python runtime declaration, interpreter consumer, container base, CI job, task, and documentation statement.
- [x] 1.3 Inventory every production/test/tool `type`, `TypeAlias`, `TypeAliasType`, `NewType`, generic parameter, deprecated typing collection, and runtime annotation-introspection use.
- [x] 1.4 Classify every production custom type as primitive, transparent alias, nominal identity, validated value object, fixed mapping, data model, or protocol.
- [x] 1.5 Inventory backend and frontend layer imports and compare documented dependency direction with executable checks.
- [x] 1.6 Inventory agent definitions, prompts, instructions, skills, hooks, MCP manifests, discovery settings, OpenSpec assets, duplicates, and stale path/tool references.
- [ ] 1.7 Run the current backend/frontend quality gates, architecture checks, OpenSpec validation, container checks, and frozen-app build to establish the pre-change baseline.
- [x] 1.8 Document deterministic repository defects separately from environment-only/tooling blockers.

## 2. Repair the Existing Baseline

- [x] 2.1 Correct the prompt-registry test source-root calculation and add a regression assertion for the resolved path.
- [x] 2.2 Reconcile the development prompt-version-set behavior and its unit test with the active configuration contract.
- [x] 2.3 Correct PyInstaller analysis data collection and remove stale nonexistent or undeclared package inputs.
- [x] 2.4 Make packaging-resource collection fail visibly rather than swallowing unsupported collection errors.
- [x] 2.5 Upgrade the frozen-app smoke from file existence to launch, bounded health polling, bundled-frontend response, and guaranteed process cleanup.
- [x] 2.6 Select and apply one canonical health endpoint across backend documentation, container, compose, frozen app, and smoke scripts.
- [ ] 2.7 Add/adjust packaging and script tests for missing resources, timeout, failed launch, successful launch, and cleanup.
- [ ] 2.8 Run the complete Python 3.12 test, lint, format, type, architecture, packaging, and pre-commit baseline.
- [ ] 2.9 Stop and report if the repaired 3.12 baseline is not green for reasons attributable to repository code.

## 3. Python 3.14 Compatibility Canary

- [x] 3.1 Install standard GIL-enabled Python 3.14 through uv without changing committed runtime policy.
- [x] 3.2 Create a disposable Python 3.14 environment from exact locked package versions with no dependency upgrades.
- [x] 3.3 Verify imports for FastAPI, Pydantic, SQLAlchemy, Strawberry, LiteLLM/OpenAI, Azure Speech, NumPy, tiktoken, PyAudioWPatch, keyboard, and PyInstaller as applicable to the platform.
- [x] 3.4 Run focused typing, scalar, retry, chat, API response, GraphQL, prompt, configuration, database, audio, and lifespan tests under Python 3.14.
- [x] 3.5 Run the complete backend test suite and architecture checks under Python 3.14.
- [x] 3.6 Build and launch the Windows frozen app under Python 3.14 using the repaired packaging path.
- [ ] 3.7 Build and health-check the production container with a Python 3.14 base.
- [ ] 3.8 Record canary failures by dependency/capability and stop the runtime cutover if any required capability lacks a viable fix.

## 4. Atomic Python 3.14 Cutover

- [ ] 4.1 Change root and backend `.python-version` files to `3.14`.
- [ ] 4.2 Change package metadata to `requires-python = ">=3.14,<3.15"`.
- [ ] 4.3 Regenerate `backend/uv.lock` from the existing lock without broad upgrade flags.
- [ ] 4.4 Compare locked package versions and document every unavoidable version change; reject unrelated churn.
- [ ] 4.5 Set Ruff target to `py314` and apply Python 3.13+/3.14 modernization findings, including defaulted generator parameters.
- [ ] 4.6 Remove stale `UP040` compatibility exceptions from root and backend Ruff configuration.
- [ ] 4.7 Set explicit Python 3.14 targets in root/backend ty configuration and tox.
- [ ] 4.8 Set the pre-commit Python runtime to 3.14.
- [ ] 4.9 Move all backend GitHub Actions and coverage jobs to Python 3.14, preferably sourcing one maintained version declaration.
- [ ] 4.10 Move production and development container bases to supported Python 3.14 images and validate image availability.
- [ ] 4.11 Add a Windows Python 3.14 frozen-build/launch smoke job to CI.
- [ ] 4.12 Add a consistency test that fails when active runtime declarations diverge.
- [ ] 4.13 Verify locked synchronization and print/assert the active Python 3.14 interpreter.

## 5. Type Semantics Modernization

- [ ] 5.1 Add executable/static fixtures demonstrating transparent alias equivalence, nominal identity rejection, and runtime validation differences.
- [ ] 5.2 Remove `PromptContent` only after source, test, generated artifact, and public documentation reference checks confirm it is unused.
- [ ] 5.3 Keep `ModelDeploymentName` transparent and document its architecture-decoupling purpose.
- [ ] 5.4 Decide and implement one semantic contract for `BaseDict` and `JSONDict`; replace known fixed shapes with explicit typed structures.
- [ ] 5.5 Prefer `Mapping`/`Sequence`/`Iterable` for read-only inputs and concrete containers for owned mutable outputs across production source.
- [ ] 5.6 Retain `MaxTokens`, `Temperature`, and `Confidence` as validated runtime scalar classes and verify bool rejection, bounds, serialization, and arithmetic behavior.
- [ ] 5.7 Audit production confidence fields and defer or implement `Confidence` adoption based on domain and serialization evidence.
- [ ] 5.8 Modernize the retry decorator alias with PEP 695 `ParamSpec` only if call signatures remain precise without casts or ignores.
- [ ] 5.9 Replace deprecated `typing` collection imports with built-ins or `collections.abc` throughout source, tests, tools, scripts, registry, and migrations where safe.
- [ ] 5.10 Confirm no legacy `TypeAlias` guidance or production use remains and no `NewType` is introduced without an opaque-identity acceptance test.
- [ ] 5.11 Update type-definition exports and tests after dead/redundant alias removal.
- [ ] 5.12 Run Ruff, ty, alias-specific tests, and full backend regression tests.

## 6. Clean Architecture Enforcement

- [ ] 6.1 Run GitNexus impact analysis before modifying each existing production symbol and record high-risk warnings before edits.
- [ ] 6.2 Define a core readiness probe port and immutable readiness result without framework imports.
- [ ] 6.3 Implement the database readiness adapter in infrastructure with structured failure diagnostics.
- [ ] 6.4 Implement application readiness orchestration over the port.
- [ ] 6.5 Wire the readiness adapter/service in composition.
- [ ] 6.6 Refactor GraphQL readiness to call the application boundary and remove the SQLAlchemy presentation import.
- [ ] 6.7 Add an import-linter contract preventing presentation imports from persistence and provider SDKs.
- [ ] 6.8 Extend architecture contract tests to require every documented layer and external-package prohibition.
- [ ] 6.9 Expose `PIIAnonymizerPort` rather than its concrete adapter from the container.
- [ ] 6.10 Add callback-aware speech-service construction to composition and remove duplicated adapter construction from lifespan orchestration.
- [ ] 6.11 Add a shared typed stream-controller dependency and replace untyped REST `app.state` access.
- [ ] 6.12 Add backend and frontend architecture checks to `task check` and `ci:local`.
- [ ] 6.13 Add the frontend architecture check to pre-commit with appropriate file scopes.
- [ ] 6.14 Re-run backend import-linter, frontend dependency checker, architecture unit tests, type checks, and affected health/lifespan/stream tests after each slice.
- [ ] 6.15 Use GitNexus changed-scope detection to confirm only expected symbols and execution flows changed.

## 7. Agent Definition and Instruction Repair

- [ ] 7.1 Define and document canonical ownership for universal policy, runtime, architecture, skills, agents, MCP manifests, hooks, and specifications.
- [ ] 7.2 Convert every Claude agent to valid client-native frontmatter, lowercase-hyphen identifiers, supported tool names, and least-privilege capabilities.
- [ ] 7.3 Ensure every portable skill has valid `name` and `description` frontmatter matching its directory.
- [ ] 7.4 Correct Python guidance to exact Python 3.14 support and the semantic custom-type taxonomy.
- [ ] 7.5 Correct all Clean Architecture skills/rules/prompts to the executable layer model and current directory names/adapters.
- [ ] 7.6 Change SDD instruction/skill paths from obsolete spec roots to main and delta OpenSpec specs.
- [ ] 7.7 Expand TDD/testing instruction scopes to both `backend/tests` and root `tests`.
- [ ] 7.8 Narrow Keploy instructions so unrelated work does not load the complete record/replay workflow.
- [ ] 7.9 Simplify prompt-file guidance to valid current frontmatter and tool identifiers.
- [ ] 7.10 Remove agent-authored Git shell commands from agents, prompts, commands, and skills; document workspace-native alternatives.
- [ ] 7.11 Correct Claude project `PYTHONPATH`, uv command policy, environment-file permissions, and stale plugin/tool permissions.
- [ ] 7.12 Resolve MCP baseline to the reproducible configured pair unless additional servers pass installation and health validation.
- [ ] 7.13 Align root and VS Code MCP manifests and remove or explicitly retire redundant legacy manifests.
- [ ] 7.14 Prevent duplicate hook registration in VS Code and extend command guarding to native PowerShell tool identities.
- [ ] 7.15 Make license-hook enforcement mode match its documentation.

## 8. Agentic De-duplication and Validation

- [ ] 8.1 Add a customization validator for frontmatter, agent names, tool vocabulary, duplicate identities, stale paths, runtime claims, architecture claims, MCP references, prohibited commands, and hook registrations.
- [ ] 8.2 Add tests/fixtures for Copilot, Claude, skill, prompt, hook, MCP, and discovery validation.
- [ ] 8.3 Declare `.github/skills` canonical and generate or hash-check any client-required mirror.
- [ ] 8.4 Configure VS Code to discover only its native Copilot instruction/skill/agent/hook surfaces.
- [ ] 8.5 Remove `.agents/skills` only after confirming no supported client requires it.
- [ ] 8.6 Remove duplicate legacy-prefixed Claude GitNexus skills after canonical identities validate.
- [ ] 8.7 Replace hook wrapper fallback copies with thin fail-closed delegates to root hook implementations.
- [ ] 8.8 Pin OpenSpec tooling instead of invoking an unbounded latest version and separate validation from destructive initialization.
- [ ] 8.9 Mark generated OpenSpec prompt/command assets or validate them against a reproducible manifest.
- [ ] 8.10 Update main OpenSpec platform requirements to match actual MCP, architecture, dependency, and agent policy.
- [ ] 8.11 Reduce always-loaded `AGENTS.md`, `CLAUDE.md`, and Copilot baseline content to stable universal/client-specific policy and move volatile inventories to generated docs.
- [ ] 8.12 Run client customization diagnostics, MCP health checks, hook fixtures, and the new repository validator before deleting any remaining duplicate surface.

## 9. Documentation and Contracts

- [ ] 9.1 Update root/backend README runtime prerequisites and exact uv commands.
- [ ] 9.2 Update contribution guidance, container docs, frozen build docs, and release checklist for Python 3.14.
- [ ] 9.3 Update active architecture diagrams/tables to match executable contracts and distinguish current from target architecture.
- [ ] 9.4 Add the custom-type decision taxonomy with examples of primitive, alias, `NewType`, value object, `TypedDict`, dataclass/model, protocol, and abstract collection.
- [ ] 9.5 Update agentic governance documentation with canonical sources, supported clients, MCP baseline, discovery rules, and validation command.
- [ ] 9.6 Update the modernization roadmap to mark Python 3.14 rollout and resolved governance/architecture work while preserving historical environment evidence.
- [ ] 9.7 Update CHANGELOG with runtime, architecture, typing, packaging, and developer-workflow changes.
- [ ] 9.8 Regenerate or verify API/GraphQL documentation and assert no unintended public contract changes.
- [ ] 9.9 Confirm repository artifacts contain no external comparison provenance or dependency.

## 10. Final Repository Verification

- [ ] 10.1 Run locked Python 3.14 synchronization from a clean environment.
- [ ] 10.2 Run Ruff lint and format checks across source, backend/root tests, tools, scripts, registry, and migrations.
- [ ] 10.3 Run ty across the configured production scope and any new typed policy tools.
- [ ] 10.4 Run backend unit, integration, property, performance, database, and full test suites.
- [ ] 10.5 Run backend import-linter and architecture policy tests.
- [ ] 10.6 Run frontend architecture, lint, typecheck, unit tests, Storybook checks, and production build.
- [ ] 10.7 Run OpenSpec strict/schema validation and customization governance validation.
- [ ] 10.8 Run security, secret, license, duplication, complexity, spelling, YAML, shell, and complete pre-commit gates.
- [ ] 10.9 Build and health-check the production container.
- [ ] 10.10 Build, launch, health-check, verify bundled UI, and stop the Windows frozen application.
- [ ] 10.11 Run full-stack smoke/e2e tests against the supported local backend/frontend ports.
- [ ] 10.12 Run GitNexus changed-scope detection and inspect every affected execution flow.
- [ ] 10.13 Run a post-change code review for correctness, security, architecture, typing, cognitive load, dead code, and docs drift.
- [ ] 10.14 Re-run all affected checks after the last code or documentation edit so completion evidence is fresh.

## 11. Release Promotion

- [ ] 11.1 Test WASAPI loopback capture on representative supported Windows hardware.
- [ ] 11.2 Test microphone capture and device selection/failure behavior.
- [ ] 11.3 Test Azure Speech authentication, recognition, transcript callback delivery, and shutdown.
- [ ] 11.4 Test configured LLM provider invocation, PII scrubbing, retry/fallback, and structured telemetry.
- [ ] 11.5 Preserve the last verified Python 3.12 container digest and desktop artifact until promotion completes.
- [ ] 11.6 Promote Python 3.14 only after all repository and hardware-dependent gates pass; otherwise execute the documented atomic rollback.
