[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

$Root = Split-Path -Parent $PSScriptRoot
$BackendDir = Join-Path $Root "backend"
$FrontendDir = Join-Path $Root "frontend"

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][scriptblock]$Action
    )

    Write-Host "`n=== $Name ===" -ForegroundColor Cyan
    & $Action
    Write-Host "[ok] $Name" -ForegroundColor Green
}

function Wait-HttpReady {
    param(
        [Parameter(Mandatory = $true)][string]$Url,
        [int]$TimeoutSeconds = 90
    )

    $start = Get-Date
    while ((Get-Date) -lt $start.AddSeconds($TimeoutSeconds)) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
                return
            }
        }
        catch {
            Start-Sleep -Milliseconds 500
            continue
        }
    }

    throw "Timeout waiting for URL: $Url"
}

function Start-Backend {
    $args = @(
        "-NoProfile",
        "-Command",
        "$env:UV_LINK_MODE='copy'; uv run uvicorn ekko.composition.app_factory:create_app --factory --host 127.0.0.1 --port 8000"
    )

    return Start-Process -FilePath "pwsh" -WorkingDirectory $BackendDir -ArgumentList $args -PassThru -WindowStyle Hidden
}

function Start-Frontend {
    $args = @(
        "-NoProfile",
        "-Command",
        "bun run dev --host 127.0.0.1 --port 5173"
    )

    return Start-Process -FilePath "pwsh" -WorkingDirectory $FrontendDir -ArgumentList $args -PassThru -WindowStyle Hidden
}

function Stop-Proc {
    param([System.Diagnostics.Process]$Process)

    if ($null -ne $Process -and -not $Process.HasExited) {
        try {
            Stop-Process -Id $Process.Id -Force -ErrorAction Stop
        }
        catch {
            Write-Warning "Failed to stop process $($Process.Id): $($_.Exception.Message)"
        }
    }
}

Invoke-Step -Name "Backend (independent) smoke" -Action {
    $backend = $null
    try {
        $backend = Start-Backend
        Wait-HttpReady -Url "http://127.0.0.1:8000/health"

        $health = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing -TimeoutSec 5
        if ($health.StatusCode -ne 200) {
            throw "Backend health endpoint returned status $($health.StatusCode)"
        }
    }
    finally {
        Stop-Proc -Process $backend
    }
}

Invoke-Step -Name "Frontend (independent) smoke" -Action {
    $frontend = $null
    try {
        $frontend = Start-Frontend
        Wait-HttpReady -Url "http://127.0.0.1:5173"

        $home = Invoke-WebRequest -Uri "http://127.0.0.1:5173" -UseBasicParsing -TimeoutSec 5
        if ($home.StatusCode -ne 200) {
            throw "Frontend home returned status $($home.StatusCode)"
        }
    }
    finally {
        Stop-Proc -Process $frontend
    }
}

Invoke-Step -Name "Frontend + Backend (together) smoke" -Action {
    $backend = $null
    $frontend = $null
    try {
        $backend = Start-Backend
        $frontend = Start-Frontend

        Wait-HttpReady -Url "http://127.0.0.1:8000/health"
        Wait-HttpReady -Url "http://127.0.0.1:5173"

        $backendHealth = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing -TimeoutSec 5
        $frontendHome = Invoke-WebRequest -Uri "http://127.0.0.1:5173" -UseBasicParsing -TimeoutSec 5

        if ($backendHealth.StatusCode -ne 200) {
            throw "Backend health returned status $($backendHealth.StatusCode)"
        }

        if ($frontendHome.StatusCode -ne 200) {
            throw "Frontend home returned status $($frontendHome.StatusCode)"
        }

        # Best-effort proxy validation: treat non-5xx as acceptable handshake response.
        try {
            $proxyCandidate = Invoke-WebRequest -Uri "http://127.0.0.1:5173/graphql" -UseBasicParsing -TimeoutSec 5
            if ($proxyCandidate.StatusCode -ge 500) {
                throw "Frontend->Backend proxy candidate returned 5xx ($($proxyCandidate.StatusCode))"
            }
        }
        catch {
            # Some stacks may return 404/405/422 depending on route/methods; do not fail unless clearly 5xx.
            if ($_.Exception.Response -and $_.Exception.Response.StatusCode.value__ -ge 500) {
                throw
            }
        }
    }
    finally {
        Stop-Proc -Process $frontend
        Stop-Proc -Process $backend
    }
}

Write-Host "`nFullstack runtime verification completed successfully." -ForegroundColor Green
