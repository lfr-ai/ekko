# Tasks: terraform-deployment-and-provider-neutral-ai

## 1. Terraform implementation

- [x] 1.1 Inventory the existing Bicep roots, modules, parameters, environment
  overrides, deployment workflow, and repository Terraform conventions.
- [x] 1.2 Add native HCL subscription and workload roots with local modules that
  mirror the existing Azure resources, dependencies, names, settings, and
  development/production differences.
- [x] 1.3 Add typed Terraform inputs, non-secret development and production
  variable examples, separate Azure Blob backend examples/state keys, and
  sensitive outputs that exclude credentials.
- [x] 1.4 Pin the tested Terraform and AzureRM versions, generate and commit
  `.terraform.lock.hcl`, and add `.tflint.hcl` with the Terraform and AzureRM
  rulesets.
- [x] 1.5 Add local Task targets and path-scoped CI checks for formatting,
  backend-free initialization/validation, and TFLint; preserve Bicep what-if
  and deploy behavior while preventing Terraform-only changes from triggering
  that workflow.

## 2. Provider-agnostic LLM implementation

- [x] 2.1 Add typed, documented settings for the default deployment, optional
  fallback deployments, generic LiteLLM API key/base/version, and opt-in cost
  tracking while preserving current OpenAI/Azure defaults.
- [x] 2.2 Route provider-qualified model names and common provider credentials
  through LiteLLM in the Infrastructure adapter; preserve already-prefixed
  deployment names and use the configured default in the summarizer.
- [x] 2.3 Replace OpenAI-specific retry exception dependencies with
  LiteLLM-normalized transient exceptions and translate exhausted failures to
  provider-neutral Core `LLMError` types at the adapter boundary.
- [x] 2.4 Configure and cache one LiteLLM Router for the configured default
  deployment and explicit fallbacks; preserve the direct-call behavior when
  fallbacks are empty or the requested model is not the configured default.
- [x] 2.5 Preserve provider-neutral success/failure telemetry and add optional
  cost observation without recording prompts or completions, keeping metrics
  implementation details in Infrastructure.

## 3. Tests and documentation

- [x] 3.1 Add focused LLM tests for typed settings, model defaults, provider
  prefixes and credentials, retry translation, cached fallback routing,
  structured-output errors, and telemetry/cost observations.
- [x] 3.2 Add Terraform checks for formatting, initialization without a backend,
  validation, and TFLint; compare Terraform resource and environment behavior
  against the existing Bicep definitions.
- [x] 3.3 Update `.env.example` and the relevant Terraform operations guide with
  configuration names, HCL workflow, TFLint commands, remote-state prerequisites,
  state sensitivity, and the no-apply boundary; add a concise Unreleased
  changelog entry.

## 4. Verification

- [x] 4.1 Run focused backend tests, configured lint/type checks, Terraform
  formatting/validation/TFLint, and applicable CI workflow checks.
- [x] 4.2 Run OpenSpec validation and resolve inconsistencies between the
  implementation and change artifacts.
- [x] 4.3 Confirm Bicep deployment behavior is unchanged, no apply was run, no
  secrets or state/plan artifacts are tracked, and all tasks are complete.
