Gap analysis: voice-bot vs golden standards (koda_automation & copier-fullstack-template)

Summary:
- voice-bot is a small, well-structured Python package under `src/voice` with FastAPI app and modular components.
- Golden repos provide comprehensive infra, CI, Taskfile, consistency checks, and a full frontend template.

Key gaps and recommended actions (exhaustive):

1) Repository governance and metadata
 - Add: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, and `CHANGELOG.md` (or keep and standardize)
 - Add: `.github/ISSUE_TEMPLATE` and `PULL_REQUEST_TEMPLATE` for consistent PRs

2) CI/CD and Release
 - CI baseline added; extend with caching, matrix builds, packaging and release automation (GitHub Releases or CI artifacts)
 - Add security scanning jobs (bandit, dependency checks) and secret detection

3) Developer experience
 - `.devcontainer` present; expand to include commonly used extensions and port-forwarding for frontend
 - Add Taskfile (done), `Makefile` shim if desired, and `scripts/` for common ops

4) Clean Architecture
 - Added skeleton packages (`core`, `application`, `infrastructure`, `presentation`) and re-export adapters
 - Next: gradually move domain logic to `core` and use interface protocols for infrastructure

5) Frontend
 - No frontend currently; copier-fullstack-template includes a frontend template — scaffold React/Vite or chosen stack and wire to FastAPI

6) IaC
 - Added `azure/iac` Bicep scaffold for core infra (ACR, Web App, Storage, Log Analytics, Cognitive Services). Key Vault is optional and disabled by default in the provided parameter files.
 - Next: add role assignments, managed identity bindings, optional Key Vault population workflows (only if Key Vault is explicitly enabled), and environment parameterization per environment

7) Tests & Quality
 - Added unit tests for managers; expand coverage to core/application modules and add integration tests
 - Add coverage reporting and threshold enforcement in CI

Action plan (priority):
1. Harden CI (linting, security scans, matrix, caching)
2. Complete Clean-Architecture refactor incrementally (move code pieces and add tests)
3. Scaffold frontend and local compose dev setup
4. Enhance IaC with RBAC and managed identity wiring, environment param files
5. Expand tests and enforce coverage
