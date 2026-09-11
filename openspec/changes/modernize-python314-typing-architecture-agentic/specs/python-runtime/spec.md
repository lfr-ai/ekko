# Delta: Python Runtime

## ADDED Requirements

### Requirement: Python 3.14 is the reproducible backend runtime
The repository MUST resolve backend development, validation, CI, container, and release tooling to standard GIL-enabled Python 3.14.

#### Scenario: Active runtime declarations agree
- GIVEN a clean checkout with supported development tools
- WHEN backend runtime metadata and automation are evaluated
- THEN every active runtime declaration selects Python 3.14
- AND package metadata rejects Python versions below 3.14 and at or above 3.15

#### Scenario: Locked dependencies install on Python 3.14
- GIVEN the committed dependency lock
- WHEN a clean Python 3.14 environment is synchronized in locked mode
- THEN synchronization succeeds without an unlocked resolution
- AND the backend and its native dependencies import successfully

### Requirement: Runtime migration preserves dependency scope
The runtime migration MUST preserve locked dependency versions unless a version change is required for Python 3.14 compatibility.

#### Scenario: Runtime lock refresh avoids unrelated upgrades
- GIVEN the pre-migration lock and the Python 3.14 package requirement
- WHEN the lock is regenerated without an upgrade request
- THEN existing package versions remain selected when compatible
- AND every changed package version has a documented Python 3.14 compatibility reason

### Requirement: Static analysis evaluates Python 3.14 semantics
The repository MUST lint and type-check Python using an explicit Python 3.14 target.

#### Scenario: Modern syntax checks are deterministic
- GIVEN the repository lint and type-check configuration
- WHEN checks run from either the repository root or backend directory
- THEN both evaluate Python 3.14 syntax and standard-library typing behavior
- AND no Python 3.12 compatibility exception suppresses a valid modernization rule

## MODIFIED Requirements

### Requirement: Python runtime support policy
The system SHALL support Python 3.14 only for backend development and production artifacts.
(Previously: the backend supported Python 3.12 only.)

#### Scenario: Unsupported interpreter is rejected
- GIVEN an interpreter other than Python 3.14
- WHEN backend dependencies are resolved from project metadata
- THEN the interpreter is rejected as unsupported
- AND the failure identifies the accepted Python range

## REMOVED Requirements

### Requirement: Python 3.12 compatibility
Python 3.12 compatibility is removed because the runtime, typing, packaging, and support policy are moving atomically to Python 3.14. The last verified Python 3.12 artifacts remain rollback assets rather than supported development targets.
