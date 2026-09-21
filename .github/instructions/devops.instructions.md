---
description: Infrastructure and operations config conventions for IaC (Bicep), the reverse proxy (Caddy), and Prometheus metrics — parameterized per-environment deploys, pinned versions, least-privilege identity, no secrets, and validate-before-apply.
applyTo: "**/*.bicep, **/*.bicepparam, **/Caddyfile, **/*.caddy"
---

# Infrastructure and operations config conventions

Validate the layers that exist (Bicep under `azure/iac/`, Caddy under
`caddy/`); do not add an alternate IaC or orchestration stack for
completeness — this repo has no Terraform. The `infrastructure-validation` and
`observability-stack` skills own the full workflows; the rules below always
apply when editing IaC or reverse-proxy config.

## Infrastructure as code (Bicep)

- Parameterize per-environment differences: the same template deploys every
  environment, differing only by a `*.bicepparam` file — never fork logic
  per environment in code.
- Pin module versions; prefer symbolic references over `resourceId()`/`reference()`.
- Mark sensitive parameters/outputs `@secure()`; use a managed identity and
  least-privilege RBAC, never embedded credentials.
- Treat a `what-if` as a review artifact — stop on any unexplained
  destructive replacement, public exposure, or broad RBAC. Agents never apply; a
  human or a separate deploy identity does.

## Reverse proxy (Caddy)

- Terminate TLS at the proxy, set security headers, bound upstream timeouts, and
  define the trusted-proxy boundary. Keep hosts and secrets in env/import files
  (`caddy/snippets/`), not inline.

## Observability (Prometheus)

- Keep metric names and labels stable and low-cardinality; see the
  `observability-stack` skill.

## Before finishing

- Run the layer's static validation (`az bicep build`, Caddy config adapt)
  before relying on the change.
