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
        uv run ty check src/ekko
    }
    finally {
        Pop-Location
    }
}

Invoke-Step -Name "Backend tests" -Action {
    Push-Location backend
    try {
        uv run python -m pytest tests -q
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

Write-Host "`n=== Workflow lint (optional local) ===" -ForegroundColor Cyan
if (Get-Command actionlint -ErrorAction SilentlyContinue) {
    actionlint -color
    Write-Host "[ok] actionlint completed" -ForegroundColor Green
}
else {
    Write-Host "[warn] actionlint not installed locally; CI workflow validates this" -ForegroundColor Yellow
}

Write-Host "`nPipeline verification completed successfully." -ForegroundColor Green
