# Proposal: terraform-deployment-and-provider-neutral-ai

## Intent

Ekko currently provisions its Azure Container Apps topology with Bicep and
uses LiteLLM behind a Core chat port, but the deployment has no Terraform
equivalent and chat retries/model defaults retain provider-specific coupling.
Provide a reviewed Terraform alternative for the existing Azure topology and
make model selection and retry handling less coupled to an individual LLM
provider without changing the current Bicep deployment path or API behavior.

## Scope

### In scope

- Mirror the existing Bicep-managed Azure resources and dev/prod parameter
  differences in Terraform/HCL.
- Isolate state per environment, use remote Azure Blob state with Entra/OIDC
  authentication, pin Terraform/provider/tool versions, and validate Terraform
  and TFLint in CI without applying infrastructure.
- Keep Bicep as the current deployment authority; document the controlled
  state-import/ownership decision required before anyone deploys Terraform
  against existing resources. Exclude Terraform-only changes from the Bicep
  workflow while leaving its what-if and deployment steps unchanged.
- Configure production use-case model deployments through typed application
  settings while preserving current defaults and provider-specific
  authentication configuration.
- Replace direct OpenAI SDK exception coupling in LiteLLM retry handling with
  LiteLLM exception types, and test retry and structured-output behavior.
- Preserve model-prefix pass-through and support failover only across explicitly
  configured deployments; do not add new provider families or implicit
  fallbacks.
- Preserve success/failure and duration observations through a Core metrics
  port, with token/cost recording opt-in and no prompt or completion data.
- Maintain Clean Architecture, environment-template, naming, test, and
  documentation conventions.

### Out of scope

- Applying Terraform, changing Azure resources, importing live state, or
  changing Bicep resource definitions, what-if behavior, or deployment steps.
- Adding a new cloud provider, changing Container Apps to another hosting
  platform, or introducing a generic IaC abstraction across clouds.
- Adding Key Vault, private networking, multi-region failover, database
  migration, persistent SQLite storage, or Redis backup resources that do not
  exist in the current Bicep topology. Record these as follow-up operational
  risks rather than silently expanding this migration.
- Adding an LLM provider family beyond the currently implemented OpenAI and
  Azure OpenAI routes. LiteLLM-prefixed model IDs remain pass-through.

## Success Criteria

- Terraform resource, output, and dev/prod parameter parity is traceable to
  the existing Bicep modules; current Bicep builds and deployment automation
  remain unchanged.
- Terraform has pinned CLI/provider/tool constraints, a committed provider
  lockfile, environment-isolated remote-state configuration, and no committed
  state or credentials.
- CI runs `terraform fmt -check`, backend-free `terraform init`/`validate`,
  and TFLint; it does not run `terraform apply`.
- The summarizer model is configurable through typed `EKKO_` settings and
  defaults to the existing deployment; the Core ChatPort remains provider-
  neutral and retry behavior no longer imports OpenAI exceptions directly.
- Explicitly configured fallback deployments use LiteLLM routing without
  changing the single-deployment default.
- LLM request observations cross the Core `MetricsPort`; token and cost metrics
  remain disabled unless explicitly configured.
- Focused tests, the full configured test suite, typecheck, architecture
  checks, Bicep validation, Terraform validation, and TFLint pass, or
  environment/baseline blockers are reported.
- A Terraform plan against existing resources is explicitly gated on an
  operator-provided state/import plan and human review; no destructive plan
  is approved by this change.

## Risks and Constraints

- Bicep and Terraform state are independent. Applying both against the same
  names could create conflicts or competing ownership. Terraform is validation-
  only until an operator establishes state ownership/import.
- Terraform state and plans can contain Redis credentials resolved from the
  Bicep-equivalent resources. Remote state access must be tightly scoped; plan
  artifacts must not be published or committed.
- Terraform and the AzureRM/TFLint versions must be mutually compatible. The
  local Terraform binary and available plugin versions constrain the initial
  compatibility range.
- The Azure best-practices MCP request was denied by the active read-only tool
  policy. Design is grounded in official Terraform provider, Microsoft Learn,
  and LiteLLM documentation; no live Azure inventory or deployment is authorized.
- Existing production Key Vault, secrets delivery, private endpoints, SQLite
  persistence, and disaster-recovery status cannot be confirmed from source
  alone. They are not assumed to exist.

## Affected Areas

- Backend: typed LLM settings, `ChatClient`, `LLMRouter`, retry handling,
  `MetricsPort`/Prometheus adapter, composition wiring, `.env.example`, and
  focused unit tests.
- Frontend: none expected.
- Infrastructure/CI: `azure/iac/terraform/`, Terraform validation tasks, and
  path-filtered CI validation; existing Bicep and deploy workflow preserved.
- Docs/Developer workflow: Terraform operations and parity guides,
  `.env.example`, validation tasks, and the Unreleased changelog.
