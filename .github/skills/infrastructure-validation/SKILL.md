---
name: infrastructure-validation
description: Validate infrastructure and operations changes across Azure/Bicep, containers, the reverse proxy, and CI/CD. Use when changing IaC, Docker/Compose, Caddy, or pipeline gates.
---

# Infrastructure validation

Validate the layers that actually exist in this repo (Bicep under `azure/iac/`,
Docker/Compose under `docker/`, Caddy under `caddy/`, GitHub Actions under
`.github/workflows/`); do not install an alternate IaC or orchestration stack
for checklist completeness — this repo has no Terraform and no Azure Pipelines.

## Workflow

1. Inventory changed deployment surfaces, environments, identities, secrets,
   rollout order, and rollback path.
2. Run static validation before credentials or deployment:
   - Bicep: `az bicep build --file azure/iac/deploy.bicep --stdout` and
     `az bicep build-params` for every `azure/iac/parameters/*/*.bicepparam`;
   - Compose: render the merged configuration and verify profiles/env inputs
     (`docker/compose.yaml` + overrides);
   - Caddy: adapt/validate the effective config (`caddy/Caddyfile`);
   - CI/CD: validate workflow YAML, triggers, permissions, and required gates.
3. Review the rendered plan/template for destructive replacement, public
   exposure, weak identity, broad RBAC, unbounded cost, and secret leakage.
4. Run read-only previews (`what-if`) only when the active identity can do so
   without applying or creating external state.
5. Hand deployment and rollback to a human or separately controlled deployment
   identity; agents never apply infrastructure changes.
6. Verify the resulting state read-only after the operator completes the change,
   then record operator-visible changes in focused docs and `.env.example`.

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

## Containers and reverse proxy

- Pin trusted base images, run as non-root, minimize build context/layers, add
  health checks, and keep secrets out of image layers and Compose files.
- Validate proxy security headers, TLS ownership, upstream timeouts, and trusted
  proxy boundaries (Caddy).
- Keep metric names/labels stable and low-cardinality (see `observability-stack`).

## CI/CD guardrails

- Validation must trigger when source, tests, agent policy, dependencies, IaC,
  containers, proxy, or pipeline definitions change.
- Separate read-only validation from deployment; deployments require explicit
  environment approval and protected credentials.
- Agents never execute Git operations or create, update, deploy, or delete
  external resources; user confirmation does not override this policy
  (AGENTS.md Hard Rule 11).
