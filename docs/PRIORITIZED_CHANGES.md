# Prioritized Changes vs Golden Standards

This document summarizes the prioritized change list derived from comparing this
repository with the golden-standard templates (`copier-fullstack-template` and
`koda_automation`) and the `claim_handler_v3` example. Items are ordered by
priority for implementation.

High priority
- CI: add rendered-tests (done), architecture enforcement (done), link and shellcheck checks (done)
- Devcontainer: add cache volumes, sensible settings and postCreateCommand (done)
- Clean Architecture enforcement: add ripgrep check (done)
- Tests: add unit/integration skeletons and ensure tests run locally (done)
- Azure IaC: add Bicep modules + deploy scripts (done)

Medium priority
- Add CONTRIBUTING.md, SECURITY.md, ISSUE and PR templates
- Add CODEOWNERS (done) and maintainers listing
- Add more integration tests and a lightweight docker-compose smoke test for rendered-tests
-- Expand documentation for deployment (secret injection via environment or platform secret stores, ACR build/push)

Low priority
- Frontend scaffold to mirror copier-fullstack-template (if project requires it)
- Full template rendering / copier usage in CI (not required for this repo)

Planned next steps
1. Add repository metadata files and templates (Contributing, Security, ISSUE/PR templates)
2. Add docker-compose smoke test and a CI job that runs it (optional)
3. Migrate remaining modules into Clean Architecture gradually
4. Expand Azure IaC with staging/prod parameter files and Key Vault secret examples
