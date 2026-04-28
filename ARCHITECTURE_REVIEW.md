# Architecture Review & Recommendations

This document contains a focused, actionable review of the `voice-bot` codebase and a prioritized set of changes to align the repository with modern, production-ready best practices and the requested "golden standard" templates.

Summary findings
- Project already follows a Clean Architecture intent: `core`, `application`, `infrastructure`, `presentation` exist and are generally separated.
- There are a number of implementation files in `models/`, `managers/`, and `infrastructure/` that should be reclassified (moved or renamed) to strictly follow dependency direction.
- Tooling (pre-commit, ruff, mypy, bandit, tests) is present but needs a few fixes (pre-commit YAML, commitizen integration, secret leakage in compose files).

High-level recommendations
1. Enforce Clean-Architecture boundaries
   - Keep `src/voice/core` framework-independent (no FastAPI, logging config, or adapters imports).
   - `application` contains use-cases and business logic and imports `core` only.
   - `infrastructure` implements protocols from `core` and must not be imported by `core` or `application`.
   - `presentation` (FastAPI) wires together the app and depends on `application` and `infrastructure`.
   - Add a CI step to run `scripts/check_clean_architecture.py` to detect import violations.

2. Simplify package layout and naming
   - Consider renaming package `voice` -> `vox` (short, modern) or `voxb` to avoid name collisions and be succinct.
   - If renaming, provide a small `scripts/rename_package.py` migration helper and update import paths in a single PR.

3. Security and secrets
   - Do not hardcode secrets in `docker` or compose files. Use `.env` and `.env.example`. Add `detect-secrets` baseline and mark false positives explicitly.
   - Ensure `.gitignore` contains `.env`, `*.key`, and other secrets (already present).

4. Dev workflow and CI
   - Use `uv` as developer toolchain and keep `pdm` as fallback in CI for reproducibility — Taskfile already updated.
   - Add Commitizen config (`.cz.toml`) and pre-commit commit-msg hook to enforce Conventional Commits and automated semantic versioning.
   - Fix YAML errors in `.github/workflows/*` (done), add frontend CI, and add Playwright E2E placeholders.

5. Packaging & distribution
   - Provide `scripts/build_exe.sh` and `scripts/build_exe.ps1` that use PyInstaller; document platform limitations (PyInstaller is not cross-platform).
   - Provide Dockerfiles for frontend and backend; avoid embedding secrets in images.

6. Infrastructure as Code (Azure)
   - Keep `azure/iac` minimal and environment-parameterized.
   - For small projects prefer: Resource Group, ACR (if building images), KeyVault (optional), App Service/Container Apps, and Log Analytics. Remove unused modules from `azure/bicep/modules` if not used by your deployment templates.
   - Follow Bicep best practices: parameterize names, avoid hardcoded regions and SKUs, and include minimal RBAC.

Concrete next steps completed in this change
- Added `.cz.toml` Commitizen configuration.
- Integrated Commitizen into `.pre-commit-config.yaml` (commit-msg hook + pre-push branch hook).
- Added `scripts/check_clean_architecture.py` (lightweight import-checker) and added an `architecture` Taskfile task.
- Added PyInstaller build scripts and `build-exe` Taskfile entry.
- Fixed `.github/workflows/codecov.yml` indentation issues.

Remaining recommended actions (follow-up PRs)
- Move modules to strict layered directories where needed and update imports.
- Add a `scripts/rename_package.py` migration if renaming package to `vox`.
- Harden Bicep templates and remove unused modules; add environment parameter files and a CI job to validate templates.
- Add Playwright E2E tests and a matching GitHub Actions workflow.
- Add more static checks in CI (ruff --fix in a controlled step, mypy strict mode increments).

References
- Clean Architecture: https://blog.cleancoder.com/uncle-bob/2011/11/22/Clean-Architecture.html
- Commitizen docs: https://commitizen-tools.github.io/commitizen/
- Ruff docs: https://docs.astral.sh/ruff/
- PyInstaller docs: https://pyinstaller.org/
- Bicep best practices: https://learn.microsoft.com/azure/azure-resource-manager/bicep/bicep-best-practices
