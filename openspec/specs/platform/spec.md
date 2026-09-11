# Ekko Platform Specification

## Purpose

Define foundational behavior expectations for Ekko as a local-first AI-assisted
voice platform.

## Requirements

### Requirement: Local development runtime availability

The system MUST expose a local backend runtime and a local frontend runtime for
interactive development.

#### Scenario: Backend and frontend are reachable locally

- GIVEN the developer has started the project in development mode
- WHEN the developer opens the configured local backend URL and frontend URL
- THEN both runtimes respond successfully
- AND local development work can proceed without cloud dependencies

### Requirement: Minimal Codecov configuration is present and enforceable

The repository MUST keep a minimal and explicit Codecov policy focused on
project-level and patch-level quality signals.

#### Scenario: Codecov configuration uses minimal required controls

- GIVEN the file `codecov.yml`
- WHEN the configuration is validated
- THEN it defines both `coverage.status.project.default` and `coverage.status.patch.default`
- AND both statuses include explicit `target` and `threshold` values
- AND coverage precision is defined in one place
- AND the configuration excludes non-product paths such as test-only directories

### Requirement: Minimal CodeRabbit configuration is present and architecture-focused

The repository MUST keep CodeRabbit configuration concise and focused on
high-signal review outcomes.

#### Scenario: CodeRabbit configuration enforces architecture and safety priorities

- GIVEN the file `.coderabbit.yaml`
- WHEN pull request review settings are evaluated
- THEN review instructions prioritize architecture violations and security issues over cosmetic style feedback
- AND style concerns already enforced by repository linters are not duplicated as primary review policy
- AND review automation remains enabled with deterministic behavior

### Requirement: Keploy usage is standardized through task wrappers

The repository MUST expose Keploy through stable task entry points instead of
ad hoc command usage.

#### Scenario: Keploy record and replay are available via task commands

- GIVEN the project task configuration
- WHEN the developer lists platform tasks
- THEN task entries exist for `keploy:record`, `keploy:test`, and `keploy:report`
- AND the record/replay workflow targets the local backend runtime
- AND the workflow can run with local-safe defaults for audio-disabled API capture

### Requirement: Structured logging provides basic observability

The application MUST use structured JSON logging for operation timing and diagnostics.
No external observability stack is required for local development.

#### Scenario: GraphQL operations are logged with timing data

- GIVEN the application is running
- WHEN a GraphQL operation completes
- THEN a structured log entry is emitted with operation name, type, duration, and status
- AND no external services (Grafana, OTel Collector) are required

### Requirement: Environment template follows the minimal project policy

The repository MUST keep `.env.example` minimal, explicit, and safe.

#### Scenario: Environment template distinguishes required, optional, and secret values

- GIVEN the file `.env.example`
- WHEN environment entries are reviewed
- THEN required runtime variables are present with empty or safe placeholder values
- AND optional variables are documented as commented optional entries where appropriate
- AND production secrets are not hardcoded with real credentials
- AND values intended for local defaults are clearly marked as local-development defaults

#### Scenario: Prompt registry strategy is explicit in environment template

- GIVEN the prompt configuration block in `.env.example`
- WHEN prompt versioning behavior is reviewed
- THEN `EKKO_PROMPT_VERSION_SET` is documented with `experimental` behavior for template-first iteration
- AND pinned prompt version behavior is documented separately from version-set behavior

### Requirement: Agentic and MCP setup parity is enforced as a baseline contract

The repository MUST keep agentic configuration parity between editor and runtime
MCP manifests.

#### Scenario: MCP server parity is preserved across repository manifests

- GIVEN `.mcp.json` and `.vscode/mcp.json`
- WHEN configured server identifiers are compared
- THEN both files contain matching definitions for `context7` and `gitnexus`
- AND workspace-specific additions remain explicitly documented and intentional

#### Scenario: Prompt-command structure remains consistent for OpenSpec workflows

- GIVEN prompt command assets under `.github/prompts/`
- WHEN OpenSpec command prompts are reviewed
- THEN a single canonical structure exists for `opsx` command prompts
- AND duplicate parallel structures are avoided to reduce maintenance and cognitive load

### Requirement: Documentation style is concise and professional

Platform and operational documentation MUST remain concise, minimal, and
professional.

#### Scenario: Documentation style avoids decorative formatting and ambiguity

- GIVEN project-facing setup and operational documentation
- WHEN documentation quality is reviewed
- THEN guidance uses direct, concrete language with explicit file/command references
- AND decorative emoji usage is avoided in baseline technical docs
- AND duplicated setup guidance across multiple files is minimized

### Requirement: GitNexus dependency for graph-based analysis is explicit

Graph-powered impact analysis workflows MUST define preconditions for usable
repository indexing.

#### Scenario: GitNexus usage expectations include index readiness

- GIVEN architecture-impact workflows that depend on GitNexus
- WHEN a repository is not indexed for the active workspace
- THEN documentation specifies the index prerequisite before graph queries are treated as authoritative
- AND fallback repository-local verification steps remain available

### Requirement: Diff-cover enforces incremental coverage quality

The repository MUST gate coverage quality on changed lines using diff-cover in
addition to project-level coverage thresholds.

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

The repository MUST define a complete, enforceable agent operating policy that
includes all hard rules, docstring conventions, and execution workflow.

#### Scenario: AGENTS.md includes all baseline hard rules

- GIVEN the file `AGENTS.md`
- WHEN the hard-rules section is reviewed
- THEN it includes rules for type safety, dataclass conventions, docstring
  format, dead code removal, architecture boundaries, cognitive load, and
  annotated-first metadata
- AND the agent profile table lists all available agent identifiers

### Requirement: Pre-commit hook surface matches baseline expectations

The repository MUST maintain a pre-commit configuration that includes all
baseline quality and security hooks without unnecessary extras.

#### Scenario: Local hooks include type checking and copy-paste detection

- GIVEN `.pre-commit-config.yaml`
- WHEN local hook definitions are reviewed
- THEN a type-check hook and a copy-paste detection hook are defined
- AND hook naming follows consistent conventions across repositories

### Requirement: Clean Architecture layer boundaries are enforced

Source code MUST follow strict layer dependency direction with no cross-layer
violations.

#### Scenario: Architecture boundary checker validates import direction

- GIVEN a boundary-checking tool configured in the repository
- WHEN it scans the source package
- THEN it reports zero violations of the inward dependency rule
- AND presentation imports only public application and core contracts
- AND presentation never imports persistence or provider SDKs directly
- AND core never imports from infrastructure or presentation

### Requirement: IaC uses subscription-scope entry with modular Bicep

The Azure IaC baseline MUST provide a subscription-scoped deployment entry point
that creates the resource group and delegates to resource-group-scoped modules.

#### Scenario: Subscription-scope deploy template creates resource group and delegates

- GIVEN `azure/iac/deploy.bicep` with `targetScope = 'subscription'`
- WHEN a deployment is executed at subscription scope
- THEN it creates or reuses a resource group named with project and environment
- AND it invokes `main.bicep` scoped to that resource group
- AND environment-specific parameters are provided from separate parameter files

#### Scenario: Resource modules are factored into reusable Bicep files

- GIVEN `azure/iac/modules/` directory
- WHEN resource definitions are reviewed
- THEN each logical Azure resource type is defined in its own module file
- AND `main.bicep` composes modules rather than defining resources inline

### Requirement: IaC parameters are environment-split using Bicep parameter files

The IaC MUST use native `.bicepparam` files organized by environment instead of
flat JSON parameter files.

#### Scenario: Environment-specific parameter files exist for each deployment target

- GIVEN `azure/iac/parameters/` directory
- WHEN parameter files are listed
- THEN at least `dev` and `prod` subdirectories exist
- AND each contains a `.bicepparam` file referencing the deploy template
- AND environment-specific values differ appropriately between dev and prod

### Requirement: IaC deployment is scripted for reproducibility

A deploy script MUST exist to orchestrate multi-environment deployment from a
single command.

#### Scenario: Deploy script invokes subscription-scope deployment for each environment

- GIVEN `azure/scripts/deploy.azcli` or equivalent deploy script
- WHEN the script is executed with a project name
- THEN it deploys the subscription-scope template for each configured environment
- AND it uses the environment-specific parameter files

### Requirement: Compiled ARM JSON is not checked into source control

The repository MUST NOT track compiled ARM JSON templates generated from Bicep
source files.

#### Scenario: No compiled ARM template JSON exists alongside Bicep source files

- GIVEN the `azure/iac/` directory
- WHEN files are listed
- THEN no `.json` files exist that are compiled outputs of `.bicep` source files
- AND the `.gitignore` or `.bicepignore` excludes generated ARM JSON

### Requirement: Container image is ACR-deployable

The container build MUST produce an image suitable for Azure Container Registry
and Azure Container Apps deployment.

#### Scenario: Containerfile builds a production image with non-root user

- GIVEN `docker/Containerfile`
- WHEN the image is built
- THEN the runtime stage runs as a non-root user
- AND the healthcheck is configured for container orchestration readiness
- AND the image entrypoint starts the application server

#### Scenario: Container Apps + ACR Bicep templates provision deployment infrastructure

- GIVEN `azure/iac/deploy.bicep` and composed modules under `azure/iac/modules/`
- WHEN the templates are deployed
- THEN they create an ACR instance, a Container Apps environment, and a Container App
- AND the Container App uses managed identity for ACR pull
- AND no admin credentials are used for ACR access

### Requirement: Docker compose port bindings use loopback addresses

Local Docker compose overrides MUST bind ports to loopback addresses only.

#### Scenario: Override compose binds to localhost

- GIVEN `docker/compose.override.yaml`
- WHEN port mappings are reviewed
- THEN all host port bindings use `127.0.0.1:` prefix
- AND no service port is bound to all interfaces for local development

### Requirement: PII protection before model calls

The system MUST scrub configured sensitive patterns before outbound LLM calls.

#### Scenario: Sensitive content is anonymized in outbound request content

- GIVEN an input containing configured PII patterns
- WHEN the input is processed for model interaction
- THEN matched sensitive values are anonymized
- AND outbound model content does not contain raw matched PII values

### Requirement: Health visibility for backend runtime

The system MUST provide a health endpoint suitable for local service checks.

#### Scenario: Health endpoint reports service availability

- GIVEN the backend runtime is started
- WHEN a request is made to the health endpoint
- THEN the endpoint returns a successful status
- AND operators can confirm service availability for local diagnostics

### Requirement: README follows minimal professional documentation style

The project README MUST be concise, factual, and free of decorative formatting.

#### Scenario: README uses minimal structure without emojis or excessive links

- GIVEN the file `README.md`
- WHEN documentation style is reviewed
- THEN section headings use plain text without emoji prefixes
- AND the quick-start section fits within a single screen
- AND external guide links are limited to essential references
- AND inline ASCII diagrams are used only when they clarify architecture

### Requirement: Docstring conventions follow Google style

Python source MUST use `"""` triple-double-quote delimiters for all docstrings
(single-line and multi-line). Single-line function/method docstrings use
imperative mood. Class docstrings use noun phrases. All multi-line docstrings
with Args, Returns, or Raises sections MUST include types.

#### Scenario: All docstrings use triple-double-quote delimiters

- GIVEN a Python source file with docstrings
- WHEN docstring delimiters are reviewed
- THEN all docstrings (single-line and multi-line) use `"""` triple-double-quote delimiters
- AND single-line function/method docstrings use imperative mood (e.g., `"""Return the user."""`)
- AND single-line class docstrings use a descriptive noun phrase (e.g., `"""A voice conversation."""`)
- AND multi-line docstrings use `"""` with typed Args/Returns/Raises sections

### Requirement: Presentation layer follows shared API contract patterns

The presentation layer MUST use consistent patterns for dependency injection,
response models, exception handling, and middleware registration.

#### Scenario: Request context wiring remains explicit and centralized

- GIVEN the GraphQL router implementation in `backend/src/ekko/presentation/graphql/router.py`
- WHEN request context construction is reviewed
- THEN context wiring for app-level dependencies is centralized in router context assembly
- AND request-scoped dependency access remains explicit and testable

#### Scenario: Response models and error constants are centralized

- GIVEN `presentation/api/responses.py`
- WHEN shared response constants are reviewed
- THEN error responses follow a canonical structure with model + examples
- AND status code constants use `fastapi.status` members

#### Scenario: Exception handlers are registered centrally without domain leakage

- GIVEN `presentation/api/exception_handlers.py`
- WHEN exception mapping is reviewed
- THEN all exception-to-response mappings are defined in one function
- AND domain internals are not exposed in production error responses

### Requirement: GraphQL layer provides a read-only query type

The GraphQL schema MUST expose a single Query root type sized for a trusted local
client. Commands use REST and live transcripts use Server-Sent Events; the schema
provides only a read-only prompt catalog.

#### Scenario: Schema includes observability extensions

- GIVEN the Strawberry GraphQL schema
- WHEN extensions are reviewed
- THEN lightweight timing and request-context extensions are configured
- AND the schema exposes only the prompt catalog query

#### Scenario: Prompt catalog supports field selection

- GIVEN the GraphQL query type
- WHEN a client queries the prompt catalog
- THEN the active version set and prompt keys are returned
- AND prompt template content is resolved only when the client selects it

### Requirement: Server-Sent Events transport delivers live transcripts

The system MUST stream live transcript segments to clients over Server-Sent
Events.

#### Scenario: Transcript stream endpoint emits transcript events

- GIVEN the backend runtime with an active transcript broadcaster
- WHEN a client connects to the transcript stream endpoint
- THEN transcript segments are delivered as Server-Sent Events
- AND connection lifecycle follows established protocol conventions

### Requirement: Dependency management uses automated update tooling

The repository MUST configure automated dependency update tooling that proposes
version bumps through pull requests.

#### Scenario: Renovate or Dependabot configuration exists and targets all ecosystems

- GIVEN dependency update configuration
- WHEN the configuration is reviewed
- THEN it targets Python (pip/uv), JavaScript (npm/bun), Docker, and GitHub Actions
- AND update frequency and grouping rules are defined

### Requirement: LLM integration uses a unified provider-agnostic adapter

The LLM chat layer MUST use a unified provider-agnostic SDK that supports
multiple providers through a single interface, following Clean Architecture
port/adapter boundaries.

#### Scenario: Chat adapter implements ChatPort using LiteLLM

- GIVEN the infrastructure LLM adapter
- WHEN the adapter is reviewed
- THEN it implements the `ChatPort` protocol defined in `core/ports/`
- AND it uses LiteLLM `completion()` / `acompletion()` for provider-agnostic calls
- AND provider routing is determined by model name prefix convention
- AND the core domain has no dependency on LiteLLM or any LLM SDK

#### Scenario: LLM adapter supports both sync and async invocation

- GIVEN a configured LLM adapter
- WHEN both sync and async chat methods are called
- THEN both return well-formed response text
- AND error handling maps provider errors to domain-appropriate exceptions

#### Scenario: LLM adapter supports retry and fallback across deployments

- GIVEN multiple LLM deployments are configured
- WHEN the primary deployment fails or is rate-limited
- THEN the adapter falls back to an alternative deployment
- AND retry behavior is configurable through settings

#### Scenario: LLM observability callbacks are configurable

- GIVEN observability integration settings
- WHEN LLM calls are made
- THEN success and failure callbacks can emit telemetry to configured sinks
- AND cost-per-request tracking is available when enabled
