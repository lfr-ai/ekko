# Review: modernize-python314-typing-architecture-agentic

## Pre-Implementation Gate

### Security

- [x] AuthN/AuthZ impact reviewed
- [x] Secret handling and data exposure reviewed
- [x] Input validation and trust boundaries reviewed

The change does not alter authentication or authorization behavior. Readiness responses continue to expose only status, not database errors or connection details. Frozen-app and container smokes use local health requests and no embedded credentials. Agent governance retains least privilege, prohibits secret collection through model-visible prompts, and strengthens command-hook coverage.

### Architecture and Maintainability

- [x] Layer boundaries respected
- [x] Coupling/cohesion impact acceptable
- [x] Migration/backward compatibility plan documented

The readiness port removes a real transport-to-persistence dependency. Composition remains the concrete wiring boundary. Type changes follow semantic intent and avoid mass nominalization. Python 3.14 is a deliberate breaking runtime floor with an atomic rollback unit and no persistence migration.

### Testing and Quality

- [x] Scenarios map to test plan
- [x] Regression strategy defined
- [x] Edge/failure cases identified

Each delta capability maps to unit, integration, static-policy, packaging, or release-smoke evidence. Failure cases include unavailable databases, missing packaging resources, unsupported interpreters, stale lockfiles, absent native wheels, invalid customizations, duplicate hooks, absent MCP capabilities, audio-device absence, speech-provider failure, and unclean process shutdown.

### Performance and Reliability

- [x] Latency/throughput risk assessed
- [x] Failure mode and recovery behavior defined
- [x] Resource usage implications reviewed

No request-path algorithmic change is planned. Readiness gains one application call around the existing probe. Python 3.14 performance is not used as an acceptance claim; behavioral and resource regressions are checked through existing performance tests and smoke behavior. Frozen-app size/startup and duplicate agent discovery are explicit regression areas.

### Documentation and DX

- [x] Developer docs update scope defined
- [x] Operational runbook implications reviewed
- [x] Contributor workflow impact documented

Runtime prerequisites, exact package-manager commands, architecture authority, type taxonomy, agent discovery, MCP baseline, quality gates, frozen build workflow, and release-native checks all require synchronized documentation. Historical evidence remains labeled historical rather than rewritten.

## Decision

- [x] Approved to implement
- [ ] Needs revision before implementation

## Notes

- Implement in phase order and stop a phase on any unexplained failure; do not stack failures across phases.
- Default MCP decision: document and validate the currently reproducible `context7` and `gitnexus` baseline. Add other servers only through a separately verified configuration change.
- Default alias decision: keep `ModelDeploymentName` transparent; remove `PromptContent` only after reference and public-contract checks; do not introduce production `NewType` unless an opaque identifier is discovered with a demonstrated interchange bug.
- Default validated-scalar decision: retain `MaxTokens`, `Temperature`, and `Confidence`; do not propagate `Confidence` through entities without a separate serialization/domain impact review.
- Default architecture decision: add presentation external-package protection and remove the verified SQLAlchemy leak. Defer a blanket application-to-adapter prohibition until current and intended use cases are explicitly modeled.
- Runtime promotion remains blocked until the Windows frozen application and representative native audio/speech checks succeed. Repository validation can complete before hardware-dependent release promotion, but it MUST report that distinction accurately.
