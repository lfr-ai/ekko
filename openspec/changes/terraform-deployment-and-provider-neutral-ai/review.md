# Review: terraform-deployment-and-provider-neutral-ai

## Pre-Implementation Gate

### Security

- [x] AuthN/AuthZ impact reviewed: CI validation needs no Azure login; remote
  state access uses Entra/OIDC and narrowly scoped Storage Blob Data permissions.
- [x] Secret handling and data exposure reviewed: credentials stay in protected
  configuration; state and plan files are sensitive and must not be committed or
  uploaded as CI artifacts; outputs must omit secrets.
- [x] Input validation and trust boundaries reviewed: Terraform variables are
  typed and validated; LiteLLM and provider SDK details remain in Infrastructure.

### Architecture and Maintainability

- [x] Layer boundaries respected: Core/Application depend on `ChatPort` and
  provider-neutral errors; LiteLLM, Router, and provider settings remain
  Infrastructure concerns.
- [x] Coupling/cohesion impact acceptable: Terraform mirrors Azure Bicep and is
  not described as cloud-neutral; HCL is limited to Terraform configuration.
- [x] Migration/backward compatibility plan documented: Bicep remains unchanged
  and authoritative for automated deployment; Terraform source is additive.

### Testing and Quality

- [x] Scenarios map to test plan: model selection, provider-prefix handling,
  error translation, fallback routing, structured responses, and Terraform
  static validation have corresponding focused checks.
- [x] Regression strategy defined: preserve existing provider defaults,
  summarization behavior, and Bicep deployment behavior when optional settings
  are absent.
- [x] Edge/failure cases identified: empty fallback configuration, exhausted
  retries, invalid structured content, distinct environment state keys, and
  Terraform-only changes entering the Bicep workflow.

### Performance and Reliability

- [x] Latency/throughput risk assessed: retries and fallback can increase tail
  latency; build and retain a configured LiteLLM Router once per application
  container, not once per request.
- [x] Failure mode and recovery behavior defined: exhausted transient failures
  become provider-neutral LLM errors; fallback is opt-in; no cloud resources are
  applied by this change.
- [x] Resource usage implications reviewed: only existing Azure resources are
  mirrored; no additional runtime service or per-request Router is planned.

### Documentation and DX

- [x] Developer docs update scope defined: update `.env.example`, Terraform
  operations guidance, and Task/CI validation commands.
- [x] Operational runbook implications reviewed: operators must configure
  remote-state storage, identity permissions, and environment protections
  before deployment; resource adoption/import and plan review remain manual.
- [x] Contributor workflow impact documented: use native HCL, run formatting,
  validation, and TFLint locally; commit `.terraform.lock.hcl`.

## Decision

- [x] Approved to implement
- [ ] Needs revision before implementation

## Notes

- The design and platform delta now specify the typed environment variables,
  retry-to-`LLMError` boundary, cached primary-to-fallback Router mapping, and
  provider-neutral telemetry with opt-in cost tracking.
- Terraform remains Azure-specific; HCL and TFLint are added without changing
  the Bicep deployment authority. Terraform CI is separately path-triggered,
  excludes remote state/plans/applies, and the Bicep deployment path excludes
  Terraform-only changes.
- State and backend examples remain operator-owned; no resource import, plan,
  or deployment is authorized by this change.
