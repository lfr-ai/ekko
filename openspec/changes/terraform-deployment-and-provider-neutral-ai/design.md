# Design: terraform-deployment-and-provider-neutral-ai

## Architecture Impact

- Impacted layers/modules:
  - Infrastructure: add an AzureRM Terraform alternative and validation workflow.
  - Configuration: add `llm_default_deployment`,
    `llm_fallback_deployments`, `litellm_api_key`, `litellm_api_base`,
    `litellm_api_version`, and `llm_track_costs` to the existing `LLMSettings`
    facet. The fallback list uses JSON array syntax in environment variables.
  - Infrastructure LLM adapter: route provider-qualified model IDs, map
    provider exceptions to the common LLM failure contract, and use LiteLLM
    routing only when fallbacks are explicitly configured. The composition
    container caches one Router for the default model and its ordered fallbacks.
  - Observability: add a Core `MetricsPort` and Infrastructure
    `PrometheusMetricsAdapter` for request outcome, duration, usage, and
    opt-in cost observations.
  - Application: preserve `ChatPort` and current use-case defaults.
- Clean Architecture boundary considerations:
  - Core/Application continue to depend on `ChatPort` and provider-neutral
    LLM exceptions and `MetricsPort` only.
  - LiteLLM types, model prefixes, credentials, Router, and provider-specific
    kwargs remain in Infrastructure.
  - Configuration remains typed `LLMSettings`; no provider SDK enters Core or
    Application.
  - Terraform is Azure-targeted because it mirrors Azure Bicep resources; this
    does not claim cloud-provider-neutral infrastructure.

## Technical Approach

- Keep the two IaC declarations side-by-side:
  - `azure/iac/terraform/` contains a subscription-scope root, a resource-group
    workload root/module composition, local modules matching the five Bicep
    modules, and separate dev/prod variable and backend examples.
  - Use native HCL in `.tf`, `.tfvars`, and `.hcl` files. Require Terraform
    `>=1.9.0,<2.0.0`, pin AzureRM to `~>4.0` with the tested version recorded in
    `.terraform.lock.hcl`, and pin TFLint and its AzureRM ruleset.
  - Use `azurerm` remote state with Entra/OIDC authentication, blob locking,
    separate `dev` and `prod` state keys, and externally supplied backend
    resource identifiers. Keep real backend files, state, plans, and secrets
    out of the repository.
  - Match resource names, SKU/scaling differences, ingress, identity/RBAC,
    logging, Redis, and application settings to Bicep. Do not add resources
    that are not present in Bicep. Require a SHA-256 image digest for production.
- Add `.tflint.hcl`, local Task targets, and a path-triggered CI workflow for
  `fmt`, backend-free `init`/`validate`, and TFLint. The validation workflow
  has no Azure login, plan, or apply step.
- Exclude `azure/iac/terraform/**` from the Bicep deployment workflow's broad
  `azure/**` path filter so Terraform-only commits cannot trigger a Bicep
  deployment. Leave Bicep what-if/deploy steps unchanged.
- Make the production summarizer model use its existing `llm_default_deployment`
  setting when configured and retain `gpt-4o-mini` when unset. The
  conversational chain continues to accept an injected `ModelDeploymentName`.
- Preserve already-prefixed LiteLLM model names. Resolve auth kwargs from the
  model's provider prefix when possible; keep the current OpenAI/Azure settings
  and use generic LiteLLM API key/base/version fields for other provider
  prefixes using those common arguments.
- Replace direct OpenAI exception imports in retry handling with LiteLLM's
  provider-normalized exception classes. Retry direct calls before mapping
  exhausted provider failures to Core `LLMError` at the adapter boundary.
- Configure fallback deployments as optional typed settings. Build the
  Router once through the composition container, configure ordered model-group
  fallback mapping, and route only the effective default deployment. Preserve
  direct calls for other model names and when the fallback list is empty. Direct
  calls use the existing Tenacity policy; the Router uses its retry count before
  moving to the next configured model group, without an extra Tenacity loop.
- Keep telemetry behind `MetricsPort`; use LiteLLM response usage and
  `completion_cost` only when `llm_track_costs` is enabled. Never record prompts
  or completions.
- Add focused coverage for configured model injection, prefixed provider auth,
  transient retry mapping, explicit fallback routing, and structured output.

## Data and Contract Changes

- API/GraphQL contract updates: none.
- Persistence/migration changes: none.
- Event/message format changes: none.
- Configuration changes: optional default deployment, JSON fallback list,
  generic provider credentials/endpoint/version, and cost tracking, all under
  `EKKO_LLM_*` or `EKKO_LITELLM_*`. Document names and defaults in
  `.env.example`; preserve current OpenAI/Azure defaults.
- Terraform variables/outputs expose the same Azure deployment choices as
  Bicep. Outputs must not expose Redis credentials or other secrets.

## Testing Strategy

- Unit:
  - Test model selection defaults and explicit configuration.
  - Test provider-prefixed model names and credential selection.
  - Test retry translation after exhausted LiteLLM failures, ordered Router
    fallback mapping, cached routing, and direct calls for empty/non-default
    cases.
  - Test valid and invalid structured output parsing.
  - Test success/failure and duration observation through `MetricsPort`, plus
    token/cost observation when tracking is enabled.
- Integration:
  - No live provider or Azure calls. Mock the LiteLLM boundary.
- End-to-end:
  - No browser/API E2E behavior changes are expected.
- Regression focus:
  - Existing OpenAI/Azure model prefixes, auth kwargs, retries, summarization,
    and Bicep deployment remain unchanged by default.

## Operability and Observability

- Preserve LLM request count and duration observations through
  `PrometheusMetricsAdapter`; optionally record response token counts and
  completion cost when configured.
- CI validates Terraform syntax and lint but does not access Azure state,
  create a plan, or deploy resources.
- Terraform state and plan output can contain resolved secrets; keep them
  remote, protected by narrow Storage Blob Data permissions, and out of CI
  artifacts.

## Rollout and Rollback

- Rollout approach:
  - Merge Terraform source and static validation without changing deployment
    ownership. Bicep remains the only automated deploy path.
  - Before any Terraform deployment to existing resources, an operator must
    configure protected remote state and import/adopt resource IDs, then
    inspect a saved plan. Do not run apply from this change.
  - Change the summarizer model only through its setting; with no override,
    current model behavior remains unchanged. Leave fallback lists empty until
    credentials and intended fallback models are explicitly configured.
- Rollback trigger:
  - Any unplanned resource replacement, production image/deployment trigger,
    changed default model, or failed provider-routing regression.
- Rollback method:
  - Revert Terraform validation/source changes while Bicep remains available.
    Restore the previous model setting/default and unset fallback configuration.
    Do not delete Terraform state or cloud resources automatically.

## Open Questions

- None for source-only implementation. Azure account, remote-state resource,
  environment protections, and production network access remain operator-owned
  deployment prerequisites and will not be inspected or changed here.
