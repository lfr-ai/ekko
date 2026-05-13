# koda_automation Golden-Standard Mapping

Last updated: 2026-05-12

## Evidence extracted

- `koda_automation/pyproject.toml`
	- Uses `uv` dependency management (`[tool.uv] package=false`, dev default group)
	- Strong dev quality toolchain: `ruff`, `ty`, `pytest`, `pre-commit`, `bandit`, `xenon`, `yamllint`
- `koda_automation/Taskfile.yml`
	- Canonical task runner commands (`task dev`, `task test`, docker workflows)
- `koda_automation/ruff.toml`
	- Explicit target version, line length, formatting profile
- `koda_automation/ty.toml`
	- Explicit root/excludes for stable static analysis
- `koda_automation/pytest.ini`
	- `testpaths = tests`, `pythonpath = src`, `asyncio_mode = auto`
- `koda_automation/.pre-commit-config.yaml`
	- Comprehensive hooks: hygiene, security, complexity, lint, type, docs, link checks
- `koda_automation/README.md`
	- Clear stack/structure/commands/config essentials
- `koda_automation/src/koda/__init__.py`
	- Package constants via `Final`, module docstring
- `koda_automation/src/koda/main.py`
	- App factory pattern, typed helper functions, documented entrypoint
- `koda_automation/src/koda/__main__.py`
	- Minimal launcher delegating to `main()`

## Standard profile distilled from koda

1. `uv` + `task` as first-class operational interface.
2. Explicit lint/type/test configs committed at repo root.
3. `pytest` source-path normalization (`pythonpath = src`).
4. Strict pre-commit quality/security gate as default workflow.
5. App-factory architecture with minimal `__main__` launcher.
6. Clean package metadata/constants in `__init__` with `Final` typing.
7. Structured docs for stack, layout, quickstart, and operations.
8. Security scanning built into routine checks (`bandit`, `detect-secrets`, `pip-audit`).
9. Complexity and duplication controls (`xenon`, `jscpd`).
10. Cross-platform developer workflow captured in Taskfile + docs.

## ekko alignment implemented

- Root `pytest.ini` hardened with `pythonpath = backend/src` for robust imports.
- Backend dependency vulnerability gate fixed by pinning `urllib3>=2.7.0`.
- `backend/.venv` rebuilt cleanly with Python 3.12 and `uv sync`.
- Full quality and security workflows executed in-session and brought to green:
	- `task check`
	- `task verify`
	- `task ci:local`
- YAML hygiene improvements applied to reduce warning noise:
	- `.warp/workflows/ekko-workflows.yaml`
	- `backend/src/ekko/ai/crewai/config/agents.yaml`
	- `docker/compose.yaml`
	- `docker/compose.override.yaml`
- Settings typing cleanup applied:
	- `backend/src/ekko/config/settings/base.py`

## Remaining optional parity work

- Enforce zero-warning yamllint policy (currently warnings are non-failing).
- Add a dedicated root task for full frontend+backend live smoke orchestration.
- Add explicit CI stage asserting independent startup of backend and frontend and combined e2e route.