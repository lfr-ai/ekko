## ADDED Requirements

### Requirement: Minimal platform tooling baseline is explicit and enforceable

The platform MUST maintain explicit, minimal configuration contracts for CI
coverage reporting, AI review automation, local replay testing, observability,
environment templates, and agentic parity.

#### Scenario: Baseline tooling contracts are discoverable in repository root and task configs

- GIVEN repository configuration files and task definitions
- WHEN a maintainer reviews platform tooling setup
- THEN the baseline contracts for Codecov, CodeRabbit, Keploy, observability, `.env.example`, and MCP parity are explicitly defined
- AND each contract can be validated without relying on undocumented conventions

### Requirement: Diff-cover enforces incremental coverage quality

The repository MUST gate coverage quality on changed lines using diff-cover.

#### Scenario: Tox coverage environment runs diff-cover after test collection

- GIVEN `tox.ini` defines a `coverage` environment
- WHEN the coverage environment runs
- THEN it produces an XML coverage report
- AND it runs `diff-cover` against the coverage report with an explicit fail-under threshold
- AND the comparison branch for diff is the main integration branch

#### Scenario: Diff-cover is available as a development dependency

- GIVEN the project dependency specification
- WHEN development dependencies are resolved
- THEN `diff-cover` is included and installable

### Requirement: Commitizen version tracking includes source file references

The commitizen configuration MUST declare which source files contain the
canonical version string.

#### Scenario: Version bump updates tracked source files

- GIVEN the file `.cz.toml`
- WHEN the commitizen configuration is reviewed
- THEN `version_files` includes the package `__init__.py` version reference

### Requirement: Prompt registry follows version-set architecture

The prompt registry MUST support named version sets with an experimental mode
that always reads from template source files.

#### Scenario: Experimental version set reads from template sources directly

- GIVEN the prompt version set is configured as `experimental`
- WHEN a prompt is requested
- THEN the prompt text is read directly from the template source
- AND no version snapshot is created or consulted

#### Scenario: Non-experimental version sets read from versioned artifacts

- GIVEN the prompt version set is configured as a named set other than `experimental`
- WHEN a prompt is requested
- THEN the prompt text is resolved from the version-set manifest
- AND the versioned prompt file is read from the versions directory

### Requirement: Agent operating policy is comprehensive and explicit

The repository MUST define a complete, enforceable agent operating policy.

#### Scenario: AGENTS.md includes all baseline hard rules

- GIVEN the file `AGENTS.md`
- WHEN the hard-rules section is reviewed
- THEN it includes rules for type safety, cast prohibition, forward reference conventions, dataclass intent, constant annotation conventions, docstring format, init return annotation, dead code removal, architecture boundaries, legacy shim prohibition, git command prohibition, language conventions, cognitive load management, and annotated-first metadata
- AND the agent profile table lists all available agent identifiers

### Requirement: Pre-commit hook surface matches baseline expectations

The repository MUST maintain a pre-commit configuration with consistent hook
naming conventions.

#### Scenario: Local type-check hook uses consistent naming

- GIVEN `.pre-commit-config.yaml`
- WHEN local hook definitions are reviewed
- THEN the type-check hook identifier follows the same naming convention used across repositories

### Requirement: GitNexus graph analysis is gated by index readiness

Graph-based impact analysis MUST require an indexed repository state before it
is considered authoritative.

#### Scenario: Index precondition is enforced for graph-based workflows

- GIVEN a graph-based analysis workflow
- WHEN the active repository is not indexed
- THEN documentation and workflow guidance require index initialization first
- AND fallback local verification steps remain available

### Requirement: Clean Architecture boundary enforcement is automated

The repository MUST include automated enforcement of layer dependency direction.

#### Scenario: Boundary checker reports zero violations on clean source tree

- GIVEN a boundary-checking tool is configured
- WHEN it scans the source package
- THEN it reports zero violations of the inward dependency rule

### Requirement: IaC uses subscription-scope entry with modular Bicep

The IaC templates MUST use a subscription-scope entry point that creates resource groups and delegates to modular Bicep files.

#### Scenario: Subscription-scope deploy template creates resource group and delegates

- GIVEN `azure/iac/deploy.bicep` with `targetScope = 'subscription'`
- WHEN a deployment is executed at subscription scope
- THEN it creates or reuses a resource group
- AND it invokes `main.bicep` scoped to that resource group

#### Scenario: Resource modules are factored into reusable Bicep files

- GIVEN `azure/iac/modules/` directory
- WHEN resource definitions are reviewed
- THEN each logical Azure resource type is in its own module file

### Requirement: IaC parameters are environment-split using Bicep parameter files

Deployment parameters MUST be split by environment using .bicepparam files.

#### Scenario: Environment-specific parameter files exist for each deployment target

- GIVEN `azure/iac/parameters/` directory
- WHEN parameter files are listed
- THEN at least `dev` and `prod` subdirectories exist with `.bicepparam` files

### Requirement: IaC deployment is scripted for reproducibility

A deploy script MUST exist for reproducible infrastructure deployments.

#### Scenario: Deploy script invokes subscription-scope deployment

- GIVEN `azure/scripts/deploy.azcli` or equivalent
- WHEN executed with a project name
- THEN it deploys for each configured environment using parameter files

### Requirement: Compiled ARM JSON is not checked into source control

Compiled ARM JSON templates MUST NOT be tracked in source control.

#### Scenario: No compiled ARM template JSON exists alongside Bicep source

- GIVEN the `azure/iac/` directory
- WHEN files are listed
- THEN no `.json` files exist that are compiled outputs of `.bicep` source files

### Requirement: Docker compose port bindings use loopback addresses

Docker compose port mappings MUST bind to loopback addresses for security.

#### Scenario: Override compose binds to localhost

- GIVEN `docker/compose.override.yaml`
- WHEN port mappings are reviewed
- THEN all host port bindings use `127.0.0.1:` prefix

### Requirement: README follows minimal professional documentation style

The README MUST follow minimal professional style without emojis.

#### Scenario: README uses minimal structure without emojis

- GIVEN the file `README.md`
- WHEN documentation style is reviewed
- THEN section headings use plain text without emoji prefixes
- AND the quick-start section fits within a single screen

### Requirement: Docstring conventions follow Google style

All Python docstrings MUST follow Google style with triple-double-quote delimiters.

#### Scenario: All docstrings use triple-double-quote delimiters

- GIVEN Python source files with docstrings
- WHEN docstring delimiters are reviewed
- THEN all docstrings (single-line and multi-line) use `"""` triple-double-quote delimiters
- AND single-line function/method docstrings use imperative mood (e.g., `"""Return the user."""`)
- AND single-line class docstrings use a descriptive noun phrase (e.g., `"""A voice conversation session."""`)

### Requirement: Presentation layer follows shared API contract patterns

The presentation layer MUST use shared patterns for DI, responses, and exception handling.

#### Scenario: Dependency registry provides typed FastAPI Depends callables

- GIVEN `presentation/api/dependency_registry.py`
- WHEN dependency providers are reviewed
- THEN container and config dependencies are exposed as typed aliases

#### Scenario: Exception handlers are registered centrally without domain leakage

- GIVEN `presentation/api/exception_handlers.py`
- WHEN exception mapping is reviewed
- THEN domain internals are not exposed in production error responses

### Requirement: GraphQL layer provides query, mutation, and subscription types

The GraphQL schema MUST include demand-control extensions for query safety.

#### Scenario: Schema includes demand-control extensions

- GIVEN the Strawberry GraphQL schema
- WHEN extensions are reviewed
- THEN query depth, alias count, token count, and query cost limits are enforced

### Requirement: Dependency management uses automated update tooling

Dependency updates MUST be automated across all managed ecosystems.

#### Scenario: Renovate or Dependabot configuration targets all ecosystems

- GIVEN dependency update configuration
- WHEN the configuration is reviewed
- THEN it targets Python, JavaScript, Docker, and GitHub Actions ecosystems

### Requirement: LLM integration uses a unified provider-agnostic adapter

The LLM chat path MUST use a unified provider-agnostic adapter implementing ChatPort.

#### Scenario: Chat adapter implements ChatPort using LiteLLM

- GIVEN the infrastructure LLM adapter
- WHEN the adapter is reviewed
- THEN it implements `ChatPort` using LiteLLM `completion()` / `acompletion()`
- AND the core domain has no dependency on LiteLLM or any LLM SDK

#### Scenario: LLM adapter supports retry and fallback across deployments

- GIVEN multiple LLM deployments
- WHEN the primary deployment fails
- THEN the adapter falls back to an alternative deployment

#### Scenario: LLM observability callbacks are configurable

- GIVEN observability integration settings
- WHEN LLM calls are made
- THEN callbacks can emit telemetry and cost tracking to configured sinks

# MODIFIED Requirements

### Requirement: Local development runtime availability

The system MUST expose local runtime workflows that remain operational with or
without optional observability services.

#### Scenario: Core local development startup works without optional observability profile

- GIVEN a local development environment
- WHEN observability profile flags are not enabled
- THEN core backend/frontend development startup remains available
- AND Prometheus/Grafana services are not required for basic development
