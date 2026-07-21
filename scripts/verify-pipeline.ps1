[CmdletBinding()]
param(
    [Parameter(HelpMessage = "Run full CI mirror mode with security scans, integration tests, and architecture check")]
    [switch]$Full
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][scriptblock]$Action
    )

    Write-Host "`n=== $Name ===" -ForegroundColor Cyan
    & $Action
    Write-Host "[ok] $Name" -ForegroundColor Green
}

# Default mode: lint, format, typecheck, unit tests
Invoke-Step -Name "Backend lint" -Action {
    Push-Location backend
    try {
        uv run ruff check src tests
    }
    finally {
        Pop-Location
    }
}

Invoke-Step -Name "Backend format check" -Action {
    Push-Location backend
    try {
        uv run ruff format --check src tests
    }
    finally {
        Pop-Location
    }
}

Invoke-Step -Name "Backend typecheck" -Action {
    Push-Location backend
    try {
        uv run ty check src/ekko
    }
    finally {
        Pop-Location
    }
}

Invoke-Step -Name "Backend unit tests" -Action {
    Push-Location backend
    try {
        uv run python -m pytest tests/unit -q
    }
    finally {
        Pop-Location
    }
}

Invoke-Step -Name "Frontend lint" -Action {
    Push-Location frontend
    try {
        bun run lint
    }
    finally {
        Pop-Location
    }
}

Invoke-Step -Name "Frontend typecheck" -Action {
    Push-Location frontend
    try {
        bun run typecheck
    }
    finally {
        Pop-Location
    }
}

Invoke-Step -Name "Frontend tests" -Action {
    Push-Location frontend
    try {
        bun run test
    }
    finally {
        Pop-Location
    }
}

Invoke-Step -Name "Frontend build" -Action {
    Push-Location frontend
    try {
        bun run build
    }
    finally {
        Pop-Location
    }
}

# Full mode: add security scans, integration tests, architecture check
if ($Full) {
    Write-Host "`n=== Full CI Mode: Security & Integration ===" -ForegroundColor Blue

    Invoke-Step -Name "Security: Bandit" -Action {
        Push-Location backend
        try {
            uv run python -m bandit -c bandit.toml -r src/ekko
        }
        finally {
            Pop-Location
        }
    }

    Invoke-Step -Name "Security: pip-audit" -Action {
        Push-Location backend
        try {
            uv run python ../scripts/security/dependency_audit.py
        }
        finally {
            Pop-Location
        }
    }

    Invoke-Step -Name "Security: detect-secrets" -Action {
        uv run python -m detect_secrets scan --baseline .secrets.baseline
    }

    Invoke-Step -Name "Integration tests" -Action {
        Push-Location backend
        try {
            uv run python -m pytest tests/integration/ -m integration -q
        }
        finally {
            Pop-Location
        }
    }

    Invoke-Step -Name "Architecture boundary check" -Action {
        uv run python tools/security/check_architecture_boundaries.py
    }
}

Write-Host "`n=== Workflow lint (optional local) ===" -ForegroundColor Cyan
if (Get-Command actionlint -ErrorAction SilentlyContinue) {
    actionlint -color
    Write-Host "[ok] actionlint completed" -ForegroundColor Green
}
else {
    Write-Host "[warn] actionlint not installed locally; CI workflow validates this" -ForegroundColor Yellow
}

Write-Host "`nPipeline verification completed successfully." -ForegroundColor Green
