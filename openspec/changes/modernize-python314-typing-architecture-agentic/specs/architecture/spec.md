# Delta: Clean Architecture

## ADDED Requirements

### Requirement: Transport health checks depend on an application boundary
Presentation code MUST obtain readiness information through an inward-facing application contract and MUST NOT construct persistence queries.

#### Scenario: Database readiness is checked without transport persistence coupling
- GIVEN a running backend with a configured database
- WHEN the readiness operation is requested through an inbound transport
- THEN the response reports database readiness
- AND the transport layer has no direct dependency on the persistence framework

### Requirement: Infrastructure construction is centralized
Runtime composition MUST be the only layer that selects and constructs concrete infrastructure and AI adapters.

#### Scenario: Streaming speech service is composed once
- GIVEN the application starts audio streaming
- WHEN a speech service with a transcript callback is required
- THEN composition creates the service through one documented construction path
- AND lifecycle orchestration does not duplicate adapter selection logic

### Requirement: Architecture checks are part of the local quality gate
Local quality commands MUST enforce backend and frontend dependency direction before work is considered complete.

#### Scenario: Local quality gate catches boundary violations
- GIVEN a source import that crosses a forbidden architecture boundary
- WHEN the standard local quality command runs
- THEN the command fails
- AND the failure identifies the violated backend or frontend dependency rule

### Requirement: Ports are exposed at dependency boundaries
When a port exists for a capability, composition and application-facing annotations MUST expose the port rather than the concrete adapter.

#### Scenario: Alternative adapter satisfies composition contract
- GIVEN a conforming replacement implementation of a core port
- WHEN it is supplied through composition
- THEN consumers type-check without depending on the original concrete implementation

## MODIFIED Requirements

### Requirement: Clean Architecture layer boundaries are enforced
Source code SHALL follow the executable inward dependency direction, permit presentation to use public core contracts, and prohibit presentation from importing persistence, AI-provider, or infrastructure implementations.
(Previously: the platform specification prohibited all presentation imports from core internals while active architecture guidance allowed public core contracts.)

#### Scenario: Architecture policy and executable checks agree
- GIVEN human-readable architecture guidance and repository boundary checks
- WHEN their layer rules are compared
- THEN they describe the same dependency direction
- AND each documented forbidden dependency is mechanically enforced

## REMOVED Requirements

### Requirement: Unenforced architecture variants
Conflicting architecture matrices and removed-layer guidance are retired because one executable dependency model is the repository authority.
