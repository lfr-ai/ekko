# Delta: Agent Governance

## ADDED Requirements

### Requirement: Agent customizations are valid for their client
Every active agent, skill, prompt, instruction, and hook registration MUST use metadata and tool identifiers supported by its discovery client.

#### Scenario: Customization validation succeeds
- GIVEN the repository customization assets for each supported client
- WHEN the customization quality gate runs
- THEN required frontmatter is present and valid
- AND agent names and tool identifiers follow the target client's schema
- AND duplicate command or agent identities are reported

### Requirement: One canonical policy owns each volatile fact
Runtime versions, architecture direction, MCP membership, and shared skill content MUST each have one declared canonical source with generated or validated adapters where client-specific copies are required.

#### Scenario: Policy mirrors cannot drift silently
- GIVEN a canonical policy and one or more client-specific mirrors
- WHEN repository validation runs
- THEN semantic or hash drift is detected
- AND the failure identifies the canonical source and stale mirror

### Requirement: Declared MCP capabilities match configured capabilities
Agent documentation and definitions MUST request only MCP capabilities configured for the applicable client.

#### Scenario: MCP parity is validated
- GIVEN repository MCP manifests and agent tool requirements
- WHEN configured server identifiers are compared
- THEN required server identifiers are present in every applicable manifest
- AND workspace-specific exceptions are explicit

### Requirement: Agent command policy is internally consistent
Agent workflows MUST NOT instruct agents to execute shell commands prohibited by repository policy.

#### Scenario: Prohibited command guidance is rejected
- GIVEN active agent, prompt, and skill text
- WHEN governance validation scans command guidance
- THEN prohibited agent-authored commands are absent
- AND supported workspace-native alternatives are documented

### Requirement: Instruction scopes target real source locations
Path-scoped instructions MUST apply to all intended files and MUST NOT target obsolete or nonexistent source roots.

#### Scenario: Test and specification guidance is discoverable
- GIVEN backend tests, root tests, and OpenSpec behavior specifications
- WHEN client instruction discovery is evaluated
- THEN test guidance covers both test roots
- AND specification guidance covers main and delta OpenSpec specifications

## MODIFIED Requirements

### Requirement: Agentic and MCP setup parity is enforced as a baseline contract
The repository SHALL keep MCP server identifiers aligned across applicable runtime manifests and shall document the capabilities actually configured.
(Previously: the platform specification required servers that were not present in the runtime manifests.)

#### Scenario: Repository manifests and documentation agree
- GIVEN the active MCP manifests and baseline agent documentation
- WHEN their server inventories are compared
- THEN the documented baseline equals the configured baseline
- AND no agent silently depends on an undeclared server

### Requirement: Agent operating policy is comprehensive and explicit
The repository SHALL keep universal hard rules concise and place client-specific execution details in client-native configuration.
(Previously: always-loaded baseline documents repeated volatile inventories and implementation details.)

#### Scenario: Baseline context contains stable policy only
- GIVEN universal and client-specific agent instructions
- WHEN responsibilities are reviewed
- THEN universal safety and architecture rules are defined once
- AND client-specific tools, counts, and discovery details are not duplicated across universal policy files

## REMOVED Requirements

### Requirement: Unmanaged triplicate skill discovery
Loading multiple unmanaged copies of the same logical skill in one client is removed because it creates ambiguous identities and contradictory context.

### Requirement: Duplicate hook execution
Registering the same hook event more than once for a client is removed because policy enforcement MUST be deterministic and non-duplicative.
