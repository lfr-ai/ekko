---
name: infrastructure-validation
description: Validate infrastructure and operations changes across Azure/Bicep or Terraform, containers, reverse proxies, observability, and CI/CD. Use when changing IaC, Docker/Compose, Caddy, Prometheus/Grafana, deployment configuration, or pipeline gates.
---

# Infrastructure validation

Validate the layers that actually exist; do not install an alternate IaC or
orchestration stack for checklist completeness.

## Workflow

1. Inventory changed deployment surfaces, environments, identities, secrets,
   state/backends, rollout order, and rollback path.
2. Run static validation before credentials or deployment:
   - Bicep: format, lint/build every entry point and parameter file;
   - Terraform, only when present: `fmt -check`, `validate`, lint, and inspect
     a saved plan (see the dedicated Terraform section below);
   - Compose: render the merged configuration and verify profiles/env inputs;
   - Caddy: adapt/validate the effective config;
   - Prometheus: validate configuration/rules; parse Grafana dashboards;
   - CI/CD: validate templates, triggers, permissions, and required gates.
3. Review the rendered plan/template for destructive replacement, public
   exposure, weak identity, broad RBAC, unbounded cost, and secret leakage.
4. Run read-only previews (`what-if` or plan) only when the active identity can
  do so without applying or creating external state.
5. Hand deployment and rollback to a human or separately controlled deployment
  identity; agents never apply infrastructure changes.
6. Verify the resulting state read-only after the operator completes the change,
  then record operator-visible changes in focused docs and environment templates.

## Azure and Bicep

- Prefer symbolic references, modules, typed parameters/outputs, and
  `*.bicepparam`; avoid `resourceId()`/`reference()` when a symbolic reference is
  available.
- Use precise user-defined or resource-derived types instead of open `object` or
  `array` when practical.
- Mark sensitive parameters/outputs `@secure()`; use managed identity and narrow
  RBAC rather than embedded credentials.
- Treat schema diagnostics as possible hallucinated resources/properties and
  verify against current Azure schemas.

## Terraform

- Pin `required_version` and every `required_providers` entry; pin module
  sources to a specific version (registry) or a fixed local path — never an
  unpinned Git ref.
- Require a remote, locked backend (state must never be committed); treat the
  state file as sensitive even when remote, since values still resolve to
  plaintext in the plan/state.
- Mark sensitive variables/outputs `sensitive = true`; source credentials from
  the provider's environment variables or a secrets manager, never literals.
- Run `terraform fmt -check`, `terraform validate`, and a linter (e.g. TFLint)
  before reviewing a saved `terraform plan`; treat any unexplained destructive
  replacement in that plan as a stop-and-ask signal, not a rubber stamp.
- Split state per environment (workspace or directory-per-environment) so one
  blast radius cannot span dev/stage/prod.

## Containers and observability

- Pin trusted base images, run as non-root, minimize build context/layers, add
  health checks, and keep secrets out of image layers and Compose files.
- `.devcontainer/` (`devcontainer.json`, `Containerfile.dev`, `compose.yml`)
  follows the same container-hygiene rules as the runtime image; validate with
  `devcontainer read-configuration` when the `@devcontainers/cli` is available,
  otherwise a Compose config render is sufficient. Its `extensions.json` is
  intentionally narrower than the host `.vscode/extensions.json` (container
  workflows omit frontend/remote-host-only extensions) — do not blind-sync
  the two lists into parity.
- Validate proxy security headers, TLS ownership, upstream timeouts, and trusted
  proxy boundaries.
- Keep metric names/labels stable and low-cardinality. Dashboards and alerts must
  query metrics the application actually emits.

## CI/CD guardrails

- Validation must trigger when source, tests, agent policy, dependencies, IaC,
  containers, proxy, observability, or pipeline definitions change.
- Separate read-only validation from deployment; deployments require explicit
  environment approval and protected credentials.
- Agents never execute Git operations or create, update, deploy, or delete
  external resources; user confirmation does not override this policy.

## Templates and references

- [`scripts/check_terraform_plan.py`](scripts/check_terraform_plan.py) — parses
  a saved `terraform show -json` plan and lists every resource with a
  destroy/replace action, so blast radius is visible before an apply.
- [`references/terraform-plan-review.md`](references/terraform-plan-review.md)
  — the manual `jq` fallback and a table of acceptable vs. stop-and-ask
  destructive changes.
