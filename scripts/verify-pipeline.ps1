Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][scriptblock]$Action
    )

    Write-Host "`n=== $Name ===" -ForegroundColor Cyan
    & $Action
    Write-Host "[ok] $Name" -ForegroundColor Green
}

Invoke-Step -Name "Backend lint" -Action {
    Push-Location backend
    try {
        uv run ruff check src tests
    }
    finally {
        Pop-Location
    }
}

Invoke-Step -Name "Backend typecheck" -Action {
    Push-Location backend
    try {
        uv run mypy --config-file mypy.ini src
    }
    finally {
        Pop-Location
    }
}

Invoke-Step -Name "Backend tests" -Action {
    Push-Location backend
    try {
        uv run pytest tests -q
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

Write-Host "`nPipeline verification completed successfully." -ForegroundColor Green
