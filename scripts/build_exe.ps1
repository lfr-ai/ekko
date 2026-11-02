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
    [switch]$Debug,
    [ValidateRange(1, 120)]
    [int]$SmokeTimeoutSeconds = 30
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

Write-Host "=== Ekko EXE Build ===" -ForegroundColor Cyan

# ── Frontend ──────────────────────────────────────────────
if (-not $SkipFrontend) {
    Write-Host "`n>> Building frontend..." -ForegroundColor Yellow
    Push-Location "$Root\frontend"
    try {
        bun install --frozen-lockfile
        bun run build
    } finally {
        Pop-Location
    }
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
try {
    $pyiArgs = @(
        "run",
        "pyinstaller",
        "--noconfirm",
        "--distpath=$Root\dist",
        "--workpath=$Root\build"
    )
    if ($Debug) {
        $pyiArgs += "--log-level=DEBUG"
    }
    $pyiArgs += "$Root\ekko.spec"

    uv @pyiArgs
} finally {
    Pop-Location
}

# ── Verify ────────────────────────────────────────────────
$exePath = "$Root\dist\ekko\ekko.exe"
if (-not (Test-Path $exePath)) {
    throw "EXE not found at $exePath"
}

Write-Host "`n>> Build successful: $exePath" -ForegroundColor Green
Write-Host "   Size: $([math]::Round((Get-Item $exePath).Length / 1MB, 1)) MB" -ForegroundColor Green

Write-Host "`n>> Smoke-testing executable..." -ForegroundColor Yellow
$listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, 0)
$listener.Start()
$smokePort = ([System.Net.IPEndPoint]$listener.LocalEndpoint).Port
$listener.Stop()

$stdoutPath = Join-Path $env:TEMP "ekko-exe-smoke-stdout-$PID.log"
$stderrPath = Join-Path $env:TEMP "ekko-exe-smoke-stderr-$PID.log"
$previousEnvironment = @{
    EKKO_DISABLE_AUDIO = $env:EKKO_DISABLE_AUDIO
    EKKO_HOST = $env:EKKO_HOST
    EKKO_OPEN_BROWSER = $env:EKKO_OPEN_BROWSER
    EKKO_PORT = $env:EKKO_PORT
    PYTHONUTF8 = $env:PYTHONUTF8
}
$process = $null

try {
    $env:EKKO_DISABLE_AUDIO = "true"
    $env:EKKO_HOST = "127.0.0.1"
    $env:EKKO_OPEN_BROWSER = "false"
    $env:EKKO_PORT = "$smokePort"
    $env:PYTHONUTF8 = "1"

    $process = Start-Process `
        -FilePath $exePath `
        -PassThru `
        -RedirectStandardOutput $stdoutPath `
        -RedirectStandardError $stderrPath

    $deadline = [DateTime]::UtcNow.AddSeconds($SmokeTimeoutSeconds)
    $healthResponse = $null
    while ([DateTime]::UtcNow -lt $deadline) {
        if ($process.HasExited) {
            throw "Executable exited before becoming healthy with code $($process.ExitCode)"
        }

        try {
            $healthResponse = Invoke-WebRequest `
                -Uri "http://127.0.0.1:$smokePort/health" `
                -UseBasicParsing `
                -TimeoutSec 2
            break
        } catch {
            [System.Threading.Thread]::Sleep(250)
        }
    }

    if ($null -eq $healthResponse -or $healthResponse.StatusCode -ne 200) {
        throw "Executable did not become healthy within $SmokeTimeoutSeconds seconds"
    }

    $frontendResponse = Invoke-WebRequest `
        -Uri "http://127.0.0.1:$smokePort/" `
        -UseBasicParsing `
        -TimeoutSec 5
    if ($frontendResponse.StatusCode -ne 200) {
        throw "Bundled frontend returned HTTP $($frontendResponse.StatusCode)"
    }

    Write-Host "   Health and bundled frontend responded successfully" -ForegroundColor Green
} catch {
    if (Test-Path $stdoutPath) {
        Write-Host "`n--- executable stdout ---" -ForegroundColor DarkYellow
        Get-Content $stdoutPath
    }
    if (Test-Path $stderrPath) {
        Write-Host "`n--- executable stderr ---" -ForegroundColor DarkYellow
        Get-Content $stderrPath
    }
    throw
} finally {
    if ($null -ne $process -and -not $process.HasExited) {
        $process.Kill($true)
        $process.WaitForExit()
    }
    foreach ($name in $previousEnvironment.Keys) {
        [System.Environment]::SetEnvironmentVariable($name, $previousEnvironment[$name], "Process")
    }
    Remove-Item $stdoutPath, $stderrPath -Force -ErrorAction SilentlyContinue
}

Write-Host "`n=== Done ===" -ForegroundColor Cyan
