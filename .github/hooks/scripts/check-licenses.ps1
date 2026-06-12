# Check Licenses — Stop hook (Windows)
# Shared script: used by both .github/hooks and .claude hooks.
# Canonical source: hooks/scripts/check-licenses.ps1
param()

# Delegate to the canonical script in hooks/scripts/
$canonical = Join-Path $PSScriptRoot "..\..\..\hooks\scripts\check-licenses.ps1"
if (Test-Path $canonical) {
    & $canonical
    exit $LASTEXITCODE
}

# Fallback: inline implementation if canonical is missing
if ($env:SKIP_LICENSE_CHECK -eq "true") { exit 0 }

$Mode = if ($env:LICENSE_MODE) { $env:LICENSE_MODE } else { "warn" }
$LogDir = if ($env:LICENSE_LOG_DIR) { $env:LICENSE_LOG_DIR } else { "logs\copilot\license-checker" }

if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }

$entry = @{ timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ"); event = "license_check_ok"; mode = $Mode } | ConvertTo-Json -Compress
Add-Content -Path "$LogDir\license.log" -Value $entry
exit 0
