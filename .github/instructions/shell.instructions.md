---
description: Shell script standards
applyTo: "**/*.zsh, **/*.sh, **/*.ps1, **/Taskfile.yml"
---

# Shell Script Conventions

## Shell Choice

### PowerShell (.ps1)
- **Use for**: Windows scripts, cross-platform automation
- **Default**: PowerShell 7+ (Core)
- **Rationale**: Better Windows support, structured objects

### Zsh (.zsh)
- **Use for**: Unix/Linux scripts, developer tooling
- **Shebang**: `#!/usr/bin/env zsh`
- **Options**: `emulate -L zsh` and `setopt ERR_EXIT PIPE_FAIL`

### POSIX shell (.sh)
- **Use for**: Portable scripts and CI/CD
- **Default shebang**: `#!/usr/bin/env sh`
- **Default options**: `set -eu`
- Use Bash and `set -euo pipefail` only when arrays, `[[ ... ]]`, `BASH_SOURCE`,
  or another documented Bash feature is required.

## PowerShell Standards

Use `#Requires -Version 7.0`, `[CmdletBinding()]`, typed `param()` blocks, and
`$ErrorActionPreference = "Stop"`. Wrap risky operations in `try`/`catch` and
`exit 1` on failure (see Error Handling below).

## Zsh Standards

`#!/usr/bin/env zsh`, then `emulate -L zsh` and `setopt ERR_EXIT PIPE_FAIL`.
Declare path constants with `readonly` (e.g. `readonly SCRIPT_DIR="${0:A:h}"`).

## POSIX sh Standards

`#!/usr/bin/env sh` with `set -eu`. Resolve the script directory portably:
`SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"`.

## Taskfile.yml

Every task declares `desc:` for discoverability. Use `deps:` for tasks that can
run in parallel, `cmds:` for sequential steps, `dir:` to change working
directory, and `silent: true` for status/help-only tasks.

## Error Handling

- **PowerShell**: wrap risky calls in `try`/`catch`, log `$_`/`$_.ScriptStackTrace`,
  `exit 1` on failure.
- **Bash/Zsh**: `set -e` (or a `trap 'handler $LINENO' ERR`) plus an explicit
  `if ! command; then ...; exit 1; fi` check for commands whose failure must be
  handled explicitly rather than just aborting.

## Common Patterns

- **Check a command exists** before using it: `command -v uv` (POSIX/Zsh) or
  `Get-Command uv -ErrorAction SilentlyContinue` (PowerShell).
- **Environment variables**: default with `${VAR:-default}` (POSIX/Zsh) or
  `$env:VAR ?? "default"` (PowerShell); require with `: "${VAR:?VAR is required}"`
  (POSIX/Zsh) or an explicit `if (-not $env:VAR) { throw "VAR is required" }`.
- **Colored output**: ANSI codes in Bash/Zsh, `Write-Host -ForegroundColor` in
  PowerShell.

## Security

- **No secrets in scripts** — load from `.env`/a secret manager, never a
  hardcoded literal value; require it explicitly
  (`export API_KEY="${API_KEY:?API_KEY not set}"`).
- **Validate input** against an explicit allow-pattern before use (for example
  `[[ "$input" =~ ^[a-zA-Z0-9_-]+$ ]]`).
- **Quote variables** (`"${file_name}"`, `"${temp_file}"`) to prevent word
  splitting on spaces — never leave a path/filename variable unquoted.

## Documentation

Every script states, at the top: a one-line synopsis, usage, each parameter,
and at least one example invocation (PowerShell: comment-based help; POSIX/Zsh:
a leading comment block).
