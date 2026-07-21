<#
.SYNOPSIS
    Build Ekko as a standalone Windows EXE (onedir).
.DESCRIPTION
    1. Builds the frontend (bun run build)
    2. Runs PyInstaller via the ekko.spec file
    3. Smoke-tests the resulting executable
#>
param(
    [switch]$SkipFrontend,
    [switch]$Debug
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

Write-Host "=== Ekko EXE Build ===" -ForegroundColor Cyan

# ── Frontend ──────────────────────────────────────────────
if (-not $SkipFrontend) {
    Write-Host "`n>> Building frontend..." -ForegroundColor Yellow
    Push-Location "$Root\frontend"
    bun install
    bun run build
    Pop-Location
    Write-Host "   Frontend built -> frontend/dist/" -ForegroundColor Green
} else {
    Write-Host "`n>> Skipping frontend build" -ForegroundColor DarkGray
}

# ── Clean previous build ─────────────────────────────────
$distDir = "$Root\dist\ekko"
if (Test-Path $distDir) {
    Write-Host "`n>> Cleaning previous build..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $distDir
}

# ── PyInstaller ───────────────────────────────────────────
Write-Host "`n>> Running PyInstaller..." -ForegroundColor Yellow
Push-Location "$Root\backend"

$pyiArgs = @("run", "pyinstaller", "--noconfirm", "$Root\ekko.spec")
if ($Debug) {
    $pyiArgs += "--log-level=DEBUG"
}

uv @pyiArgs
Pop-Location

# ── Verify ────────────────────────────────────────────────
$exe = "$Root\dist\ekko\ekko.exe"
if (Test-Path $exe) {
    Write-Host "`n>> Build successful: $exe" -ForegroundColor Green
    Write-Host "   Size: $([math]::Round((Get-Item $exe).Length / 1MB, 1)) MB" -ForegroundColor Green
} else {
    Write-Host "`n>> ERROR: EXE not found at $exe" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Done ===" -ForegroundColor Cyan
