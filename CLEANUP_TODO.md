# 🎯 COMPREHENSIVE CLEANUP TODO

## Priority 1: Critical Configuration Files

- [ ] Add pytest.ini
- [ ] Add .coveragerc
- [ ] Add ty.toml
- [ ] Add bandit.toml
- [ ] Update .typos.toml
- [ ] Update .gitignore (comprehensive)
- [ ] Clean pyproject.toml (UV settings only)
- [ ] Remove either Renovate OR Dependabot
- [ ] Add CHANGELOG.md

## Priority 2: Docker & DevContainer

- [ ] Update .devcontainer/devcontainer.json
- [ ] Update .devcontainer/compose.yml
- [ ] Create/update Containerfile.dev
- [ ] Add Caddy for local development
- [ ] Update docker-compose.yml
- [ ] Clean Dockerfile
- [ ] Add .dockerignore
- [ ] Add .containerignore

## Priority 3: GitHub Actions & CI/CD

- [ ] Review and fix GitHub Actions workflows
- [ ] Add pre-push verification script
- [ ] Update PR template
- [ ] Test CI pipeline locally
- [ ] Ensure all tests pass in CI
- [ ] Add workflow status badges

## Priority 4: Testing

- [ ] Add comprehensive unit tests
- [ ] Add integration tests
- [ ] Add property-based tests (Hypothesis)
- [ ] Add E2E tests (Playwright)
- [ ] Add tests for registry module
- [ ] Ensure 70%+ coverage
- [ ] Add test factories
- [ ] Add test fixtures

## Priority 5: Frontend

- [ ] Update frontend dependencies
- [ ] Add comprehensive component tests
- [ ] Ensure shadcn/ui best practices
- [ ] Add Storybook stories
- [ ] Add E2E tests with Playwright
- [ ] Update routing
- [ ] Check UX/UI best practices

## Priority 6: Clean Architecture Verification

- [ ] Verify all layer boundaries
- [ ] Check imports direction
- [ ] Ensure core has no external deps
- [ ] Test dependency injection
- [ ] Verify protocols usage

## Priority 7: Code Quality

- [ ] Run ruff format on all Python files
- [ ] Run biome format on all TS files
- [ ] Fix all linting issues
- [ ] Fix all type errors
- [ ] Remove unused imports
- [ ] Remove dead code
- [ ] Update docstrings

## Priority 8: Documentation

- [ ] Update README.md
- [ ] Update CONTRIBUTING.md
- [ ] Add/update API documentation
- [ ] Update architecture diagrams
- [ ] Add deployment guide
- [ ] Update changelog

## Priority 9: Tool Setup Verification

- [ ] Verify CodeRabbit configuration
- [ ] Verify GitNexus configuration
- [ ] Verify Warp workflows
- [ ] Test Claude via GitHub Copilot
- [ ] Verify all VS Code settings
- [ ] Test all Task commands

## Priority 10: Final Verification

- [ ] Run full quality check: task check
- [ ] Test development setup: task dev
- [ ] Build production: task build:exe
- [ ] Verify all documentation links
- [ ] Test in clean environment
- [ ] Create deployment checklist

---

**Estimated Time**: 6-8 hours
**Status**: 🟡 In Progress
**Last Updated**: 2026-05-02
