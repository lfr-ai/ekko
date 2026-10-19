# Lessons

Proven gotchas and their recoveries. One entry per lesson; include the
evidence (file, command, or check) that verified it. Remove an entry once it
is stale (the cited file moved/deleted, or the underlying tool changed).

- Windows/OneDrive: `uv run` env vars must be set via `$env:NAME='value'; uv ...`
  in PowerShell, not POSIX-style `NAME=value uv ...` — the latter fails
  silently on Windows tasks. See [Taskfile.yml](../Taskfile.yml).
- `backend/tests` and root `tests/` cannot be invoked in one pytest run (both
  ship a `conftest.py`, causing `ImportPathMismatchError`); run them from their
  respective directories separately.
- Pytest 9 renamed `xfail_strict` to `strict_xfail` (the old name remains an
  alias). Use the current name in both config files; verify with `pytest --help`
  and the [pytest configuration reference](https://docs.pytest.org/en/stable/reference/reference.html#confval-strict_xfail).
- Run naming guards against every source root in `PROJECT.md`; root-only
  defaults can pass without scanning a backend under `backend/src`.
