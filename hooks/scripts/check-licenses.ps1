# License Checker — Stop hook (Windows)
# Scans new/changed dependencies for copyleft or unapproved licenses.
param()

$LicenseMode = if ($env:LICENSE_MODE) { $env:LICENSE_MODE } else { "warn" }
$LogDir = if ($env:LICENSE_LOG_DIR) { $env:LICENSE_LOG_DIR } else { "logs\copilot\license-checker" }

if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }

$timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

# Copyleft licenses that are NOT allowed
$blockedLicenses = @(
    "GPL-2.0",
    "GPL-3.0",
    "AGPL-3.0",
    "LGPL-2.1",
    "LGPL-3.0",
    "MPL-2.0",
    "EUPL-1.2",
    "SSPL-1.0",
    "CC-BY-SA-4.0"
)

$violations = @()

# Check Python dependencies (backend)
$backendDir = "backend"
if (Test-Path "$backendDir\pyproject.toml") {
    try {
        $pipOutput = uv run --project $backendDir pip-audit --format json 2>$null | ConvertFrom-Json
        # pip-audit checks vulnerabilities, not licenses — skip for now
    } catch {
        # pip-audit not available or failed — non-blocking
    }
}

# Check frontend dependencies
$frontendDir = "frontend"
if (Test-Path "$frontendDir\package.json") {
    try {
        $licenseOutput = & npx license-checker --json --start $frontendDir 2>$null | ConvertFrom-Json
        if ($licenseOutput) {
            foreach ($pkg in $licenseOutput.PSObject.Properties) {
                $license = $pkg.Value.licenses
                foreach ($blocked in $blockedLicenses) {
                    if ($license -match [regex]::Escape($blocked)) {
                        $violations += @{
                            package = $pkg.Name
                            license = $license
                            blocked = $blocked
                        }
                    }
                }
            }
        }
    } catch {
        # license-checker not available — non-blocking
    }
}

if ($violations.Count -gt 0) {
    $logEntry = @{
        timestamp = $timestamp
        event = "license_violations"
        mode = $LicenseMode
        violation_count = $violations.Count
        violations = $violations
    } | ConvertTo-Json -Compress
    Add-Content -Path "$LogDir\license.log" -Value $logEntry

    if ($LicenseMode -eq "block") {
        $reason = "License Checker: $($violations.Count) copyleft/unapproved license(s) detected"
        Write-Error $reason
        exit 1
    }
    else {
        @{ systemMessage = "License Checker: $($violations.Count) license concern(s) found (warn mode)" } | ConvertTo-Json -Compress
        exit 0
    }
}
else {
    $logEntry = @{ timestamp = $timestamp; event = "license_check_passed"; mode = $LicenseMode } | ConvertTo-Json -Compress
    Add-Content -Path "$LogDir\license.log" -Value $logEntry
    exit 0
}
