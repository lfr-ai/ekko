---
name: pyinstaller
description: Package a Python app into a standalone executable with PyInstaller — .spec files, onefile vs onedir, hidden imports, bundled data, reproducible builds, and locating resources at runtime. Use when shipping a CLI or desktop .exe or a self-contained binary.
---

# PyInstaller packaging

Freeze a Python entry point into a self-contained executable. A committed
spec is typically `<project>.spec` (root, see `PROJECT.md`), building the
desktop distribution via `task build:exe` / `scripts/build_exe.ps1`. Keep the
frozen entry point thin and import real logic from the package so it stays
testable without freezing.

## The spec file is the source of truth

- `<project>.spec` is executable Python and pins every build option. Rebuild
  with `pyinstaller <project>.spec` (or `task build:exe`); CLI options are
  ignored when
  building from a spec (only `--clean`, `--noconfirm`, `--distpath`,
  `--workpath`, `--log-level`, `--upx-dir` still apply).
- The spec builds `Analysis` -> `PYZ` -> `EXE` (plus `COLLECT` for onedir). Keep
  `data`, `binaries`, `hiddenimports`, and `excludes` as named lists above the
  `Analysis` call for readability.

## onefile vs onedir

| | onefile | onedir |
| --- | --- | --- |
| Output | one `.exe` | folder with `.exe` + deps |
| Startup | slower (unpacks to a temp dir each run) | faster |
| Signing / AV | harder | easier (sign the folder) |
| Use for | frictionless single-file hand-off | most production tools |

Prefer onedir for anything code-signed or frequently started; use onefile only
for simple single-file distribution.

## Bundling data and hidden imports

- Add non-code resources via `data=[("src/templates", "templates")]`
  (source path, run-time folder). Data files (images, `.json`, `.md`) go in
  `data`; shared libraries (`.dll`/`.so`/`.dylib`) go in `binaries`.
- Add imports PyInstaller cannot detect (plugins, dynamic `importlib`,
  side-effect modules) to `hiddenimports`, or use `collect_submodules` /
  `collect_data_files` from `PyInstaller.utils.hooks`.
- Trim size with `excludes=[...]` for unused heavy deps (tests, `tkinter`).

## Locate resources at run time

The working directory is not the bundle. Resolve bundled paths through
`sys._MEIPASS` (set when frozen) with a source fallback:

```python
import sys
from pathlib import Path


def resource_path(relative: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    return base / relative
```

For data inside an installed package, prefer `importlib.resources` /
`pkgutil.get_data` over manual paths.

## Reproducible, debuggable builds

- Pin a fixed hash seed for determinism via the `EXE` `OPTIONS` list:
  `[("hash_seed=0", None, "OPTION")]`; build with `--clean` in CI.
- Support debug and production builds from one spec with an argparse block and
  `pyinstaller <project>.spec -- --debug` (console + onedir for debug, windowed
  onefile for release).
- Never bundle secrets or `.env` into the binary — read configuration at run
  time (AGENTS.md Hard Rule: no secrets in code).

## Guardrails

- Test the built binary on a clean machine/VM with no Python installed — imports
  that work in dev often miss from the freeze.
- Freeze on each target OS; PyInstaller does not cross-compile.
- Keep the `.spec`, the `data` manifest, and `task build:exe` in version control.
