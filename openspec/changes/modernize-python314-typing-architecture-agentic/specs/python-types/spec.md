# Delta: Python Type Semantics

## ADDED Requirements

### Requirement: Custom types express their intended semantics
Every production custom type MUST use the least complex construct that enforces its intended distinction.

#### Scenario: Transparent shape uses a type alias
- GIVEN a recurring compound annotation whose values remain interchangeable with the underlying type
- WHEN a custom name is introduced
- THEN it is declared as a PEP 695 type alias
- AND static callers may use values of the underlying type directly

#### Scenario: Opaque identifier uses nominal typing
- GIVEN two identifiers share the same runtime representation but MUST NOT be interchanged statically
- WHEN the identifiers cross a typed boundary
- THEN each identity is represented by a distinct nominal type
- AND the type checker rejects passing the underlying primitive without explicit construction

#### Scenario: Runtime invariant uses validation
- GIVEN a value has a range, format, or business invariant that MUST hold at runtime
- WHEN the value is created
- THEN invalid input is rejected at construction
- AND the construct is not represented solely by a transparent alias or static nominal wrapper

#### Scenario: Fixed mapping shape uses named fields
- GIVEN a mapping has a known set of keys and field-specific value types
- WHEN it is exposed through a typed boundary
- THEN the keys and value types are represented explicitly
- AND a generic string-to-object dictionary does not hide the known schema

### Requirement: `NewType` is static-only
The repository MUST treat `NewType` as a zero-validation static identity mechanism.

#### Scenario: Nominal wrapper preserves runtime value
- GIVEN a value wrapped by a nominal type
- WHEN it is evaluated at runtime
- THEN the wrapped object is returned unchanged
- AND runtime validation is not inferred from the wrapper

### Requirement: Public aliases are used and semantically distinct
A public type alias MUST have active consumers and MUST NOT duplicate another public alias without a distinct contract.

#### Scenario: Alias inventory is validated
- GIVEN the production type-definition modules
- WHEN public aliases and their references are audited
- THEN unused documentation-only aliases are absent
- AND two public names do not expose identical semantics unless their distinction is specified and tested

## MODIFIED Requirements

### Requirement: Python alias syntax
The system SHALL declare transparent aliases with the `type` statement and use modern type-parameter syntax for generic aliases and functions.
(Previously: agent guidance also demonstrated assignment-style aliases and deprecated `TypeAlias` patterns.)

#### Scenario: Guidance and source agree
- GIVEN production aliases and active Python guidance
- WHEN alias examples are reviewed
- THEN all modern examples use PEP 695 syntax
- AND no active guidance recommends `Any` as the value type of a generic JSON dictionary

## REMOVED Requirements

### Requirement: Blanket dictionary-alias policy
The requirement to use a generic dictionary alias for every string-keyed mapping is removed. Known schemas use explicit typed structures, read-only inputs prefer abstract mappings, and generic aliases remain only for truly open shapes.
