# Delta: Desktop Packaging

## ADDED Requirements

### Requirement: Windows frozen application is release-verifiable
The Windows desktop artifact MUST be built and smoke-tested on the supported Python runtime before release.

#### Scenario: Frozen application launches and serves bundled UI
- GIVEN a clean Windows Python 3.14 build environment and a built frontend
- WHEN the frozen application is built and launched
- THEN its health endpoint becomes successful within a bounded interval
- AND the bundled frontend is reachable
- AND the process terminates cleanly after the smoke test

### Requirement: Packaging inputs match declared capabilities
The frozen-app specification MUST collect only resources and packages that exist in the supported application configuration.

#### Scenario: Stale package collection fails validation
- GIVEN a package or data directory is absent from the declared application dependencies
- WHEN packaging configuration is validated
- THEN the stale collection entry is rejected or removed
- AND packaging does not silently swallow the mismatch

### Requirement: Native desktop integrations have release gates
Native audio capture and speech recognition MUST be verified on representative Windows hardware before production promotion.

#### Scenario: Release candidate exercises native integrations
- GIVEN a Python 3.14 release candidate artifact on supported Windows hardware
- WHEN the desktop release checklist is executed
- THEN loopback capture, microphone capture, speech recognition, transcript delivery, and clean shutdown succeed
- AND a failed native integration blocks production promotion

## MODIFIED Requirements

### Requirement: Container and desktop health checks use the canonical endpoint
All deployment and packaging smokes SHALL use one documented backend health endpoint.
(Previously: container definitions referenced inconsistent health paths.)

#### Scenario: Health probes agree
- GIVEN container, compose, and frozen-app health configuration
- WHEN their probe targets are compared
- THEN they use the same canonical health endpoint
- AND each probe succeeds against a running artifact

## REMOVED Requirements

### Requirement: File-existence-only executable smoke
A build is no longer considered verified merely because an executable file exists; launch and health behavior replace that check.
