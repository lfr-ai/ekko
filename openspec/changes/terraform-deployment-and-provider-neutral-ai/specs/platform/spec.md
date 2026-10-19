# Delta: platform

## MODIFIED Requirements

### Requirement: LLM integration uses a unified provider-agnostic adapter

The LLM chat layer MUST use a unified provider-agnostic SDK that supports
multiple providers through a single interface, following Clean Architecture
port/adapter boundaries. Each application use case MUST allow its LiteLLM
deployment name to be configured without introducing provider SDK dependencies
into Core or Application.

#### Scenario: Chat adapter implements ChatPort using LiteLLM

- GIVEN the infrastructure LLM adapter
- WHEN the adapter is reviewed
- THEN it implements the `ChatPort` protocol defined in `core/ports/`
- AND it uses LiteLLM completion APIs for provider-agnostic calls
- AND provider routing is determined by the LiteLLM model name prefix
- AND already-prefixed deployment names are passed through unchanged
- AND the Core layer has no dependency on LiteLLM or any LLM SDK

#### Scenario: Application model deployments are configurable

- GIVEN the default model deployment for a use case
- WHEN a deployment override is configured
- THEN the configured model name is used for that use case
- AND when no override is supplied, the existing default model behavior is preserved

#### Scenario: LLM adapter supports both sync and async invocation

- GIVEN a configured LLM adapter
- WHEN both sync and async chat methods are called
- THEN both return well-formed response text
- AND provider failures are translated to provider-neutral LLM errors at the
  Infrastructure boundary

#### Scenario: LLM adapter retries transient provider failures

- GIVEN a transient LiteLLM provider failure
- WHEN the chat adapter invokes a deployment
- THEN the configured retry policy is applied
- AND provider SDK exception classes do not leak into Core or Application

#### Scenario: LLM adapter falls back only when alternatives are configured

- GIVEN a primary deployment and one or more explicit fallback deployments
- WHEN the primary deployment remains unavailable after its retry policy
- THEN LiteLLM routes the request to a configured fallback deployment
- AND the composition container reuses one configured Router
- AND requests for non-default models bypass the Router
- AND when no fallback deployment is configured, the adapter preserves the
  current single-deployment behavior

#### Scenario: LLM telemetry stays provider-neutral

- GIVEN a chat adapter with a configured `MetricsPort`
- WHEN a completion succeeds or fails
- THEN the adapter records the outcome and duration through the port
- AND the Core port does not expose Prometheus or LiteLLM types
- AND prompts and completion content are never recorded

#### Scenario: Token and cost tracking is opt-in

- GIVEN `llm_track_costs` is disabled
- WHEN a completion returns token usage
- THEN the adapter does not record token usage or cost
- WHEN `llm_track_costs` is enabled
- THEN the adapter records response token usage and LiteLLM completion cost
  through `MetricsPort`

#### Scenario: LLM adapter validates structured output

- GIVEN an asynchronous structured completion request
- WHEN LiteLLM returns valid structured content
- THEN the adapter returns the validated response model
- AND when the content cannot be validated, the adapter raises a
  provider-neutral LLM error
