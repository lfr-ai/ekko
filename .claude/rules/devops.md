---
paths:
  - "**/*.bicep"
  - "**/*.bicepparam"
  - "**/*.tf"
  - "**/*.tfvars"
  - "**/Caddyfile"
  - "**/*.caddy"
  - "**/prometheus*.yml"
  - "**/prometheus*.yaml"
  - "**/grafana/**"
---

# Infrastructure and operations config conventions

Validate the layers that exist; do not add an alternate IaC or orchestration
stack for completeness. The `infrastructure-validation` and `observability-stack`
skills own the full workflows; the rules below always apply when editing IaC,
reverse-proxy, or observability config. Read the deploy targets from `PROJECT.md`.

## Infrastructure as code (Bicep/Terraform)

- Parameterize per-environment differences: the same template deploys every
  environment, differing only by a parameter/variable file — never fork logic
  per environment in code.
- Pin module and provider versions; require a remote, locked state backend for
  Terraform and never commit state.
- Mark sensitive parameters/outputs (`@secure()` / `sensitive = true`); use a
  managed identity and least-privilege RBAC, never embedded credentials.
- Treat a `what-if`/plan as a review artifact — stop on any unexplained
  destructive replacement, public exposure, or broad RBAC. Agents never apply; a
  human or a separate deploy identity does.

## Reverse proxy (Caddy/nginx)

- Terminate TLS at the proxy, set security headers, bound upstream timeouts, and
  define the trusted-proxy boundary. Keep hosts and secrets in env/import files,
  not inline.

## Observability (Prometheus/Grafana)

- Keep metric names and labels stable and low-cardinality; dashboards and alerts
  must query metrics the app actually emits.
- Provision dashboards and datasources as code, not hand-edited in the UI.

## Before finishing

- Run the layer's static validation (Bicep build, `terraform validate`, or a
  config render) before any credentialed step, and update the owning operational
  doc and env templates when operator-visible behavior changes.
