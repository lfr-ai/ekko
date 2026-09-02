---
paths:
  - "**/*.zsh"
  - "**/*.sh"
  - "**/*.ps1"
  - "**/Taskfile.yml"
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

### Bash (.sh)
- **Use for**: Portable POSIX scripts, CI/CD
- **Shebang**: `#!/usr/bin/env bash`
- **Options**: `set -euo pipefail`

## PowerShell Standards

```powershell
#Requires -Version 7.0

<#
.SYNOPSIS
    Brief description of what the script does.

.DESCRIPTION
    Detailed description.

.PARAMETER ParameterName
    Description of parameter.

.EXAMPLE
    ./script.ps1 -ParameterName value
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$RequiredParam,

    [Parameter(Mandatory=$false)]
    [string]$OptionalParam = "default"
)

$ErrorActionPreference = "Stop"

# Script body
try {
    Write-Verbose "Starting operation..."
    # ... operations
    Write-Output "Success"
} catch {
    Write-Error "Operation failed: $_"
    exit 1
}
```

## Zsh Standards

```zsh
#!/usr/bin/env zsh
# Script description

emulate -L zsh
setopt ERR_EXIT PIPE_FAIL

# Constants
readonly SCRIPT_DIR="${0:A:h}"
readonly PROJECT_ROOT="${SCRIPT_DIR}/.."

# Functions
function main() {
    local arg1="$1"
    local arg2="${2:-default}"

    # Implementation
    echo "Processing: ${arg1}"
}

# Entry point
main "$@"
```

## Bash Standards

```bash
#!/usr/bin/env bash
# Script description

set -euo pipefail

# Constants
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="${SCRIPT_DIR}/.."

# Functions
main() {
    local arg1="$1"
    local arg2="${2:-default}"

    # Implementation
    echo "Processing: ${arg1}"
}

# Entry point
main "$@"
```

## Taskfile.yml

### Structure
```yaml
version: '3'

vars:
  PROJECT_NAME: myapp
  PYTHON_VERSION: '3.13'

includes:
  backend:
    taskfile: ./tasks/backend.yml
    dir: .

tasks:
  default:
    desc: Show available tasks
    cmds:
      - task --list

  install:
    desc: Install all dependencies
    cmds:
    - uv sync
      - task: backend:install

  test:
    desc: Run all tests
    cmds:
      - task: backend:test

  lint:
    desc: Run all linters
    cmds:
      - task: backend:lint

  check:
    desc: Run all checks (lint + test)
    deps:
      - lint
      - test
```

### Task Best Practices
1. **Always add `desc:`** for discoverability
2. **Use `deps:`** for dependencies (run in parallel)
3. **Use `cmds:`** for sequential commands
4. **Use `dir:`** to change working directory
5. **Use `silent: true`** for status/help tasks

## Error Handling

### PowerShell
```powershell
try {
    # Risky operation
    Invoke-Command -ScriptBlock { ... }
} catch {
    Write-Error "Operation failed: $_"
    Write-Error $_.ScriptStackTrace
    exit 1
}
```

### Bash/Zsh
```bash
# Exit on error
set -e

# Custom error handler
function error_handler() {
    echo "Error on line $1" >&2
    exit 1
}
trap 'error_handler $LINENO' ERR

# Risky operation
if ! command_that_might_fail; then
    echo "Command failed" >&2
    exit 1
fi
```

## Common Patterns

### Check Command Exists
```bash
# Bash/Zsh
if ! command -v uv >/dev/null 2>&1; then
    echo "Error: uv not found" >&2
    exit 1
fi
```

```powershell
# PowerShell
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Error "uv not found"
    exit 1
}
```

### Environment Variables
```bash
# Bash/Zsh with default
DATABASE_URL="${DATABASE_URL:-postgresql://localhost/myapp}"

# Required variable
: "${DATABASE_URL:?DATABASE_URL is required}"
```

```powershell
# PowerShell with default
$DatabaseUrl = $env:DATABASE_URL ?? "postgresql://localhost/myapp"

# Required variable
if (-not $env:DATABASE_URL) {
    throw "DATABASE_URL is required"
}
```

### Colored Output
```bash
# Bash/Zsh
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Success${NC}"
echo -e "${RED}Error${NC}"
```

```powershell
# PowerShell
Write-Host "Success" -ForegroundColor Green
Write-Host "Error" -ForegroundColor Red
Write-Host "Warning" -ForegroundColor Yellow
```

## Security

### No Secrets in Scripts
```bash
# Bad
export API_KEY="secret123" # pragma: allowlist secret

# Good: Load from secure source
source .env
export API_KEY="${API_KEY:?API_KEY not set}"
```

### Input Validation
```bash
# Good: Validate input
if [[ ! "$input" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    echo "Invalid input" >&2
    exit 1
fi
```

### Use Quoted Variables
```bash
# Good: Prevents word splitting
echo "Processing: ${file_name}"
rm "${temp_file}"

# Bad: Vulnerable to spaces in filenames
echo "Processing: $file_name"
rm $temp_file
```

## Documentation

Every script must have:
1. **Synopsis**: One-line description at top
2. **Usage**: How to run the script
3. **Parameters**: What each parameter does
4. **Examples**: At least one usage example

```bash
#!/usr/bin/env bash
# Deploy application to specified environment
#
# Usage:
#   ./deploy.sh <environment> [--force]
#
# Parameters:
#   environment: Target environment (local, dev, prod)
#   --force: Skip confirmation prompts
#
# Examples:
#   ./deploy.sh dev
#   ./deploy.sh prod --force
```
