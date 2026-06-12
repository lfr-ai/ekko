# Tool Guardian — PreToolUse hook (Windows)
# Blocks dangerous tool operations before the Copilot coding agent executes them.
# Enforces repository rule that agents never run git shell commands.
param()

if ($env:SKIP_TOOL_GUARD -eq "true") { exit 0 }

$GuardMode = if ($env:GUARD_MODE) { $env:GUARD_MODE } else { "block" }
$LogDir = if ($env:TOOL_GUARD_LOG_DIR) { $env:TOOL_GUARD_LOG_DIR } else { "logs\copilot\tool-guardian" }

if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }

$input_json = $input | Out-String
try { $data = $input_json | ConvertFrom-Json } catch { exit 0 }

$toolName = $data.tool_name
$toolInput = if ($data.tool_input -is [string]) { $data.tool_input } else { $data.tool_input | ConvertTo-Json -Compress }
$scanText = "$toolName $toolInput"
$isCommandTool = $toolName -eq "run_in_terminal" -or $toolName -eq "Bash"

$timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

# Threat patterns: category, severity, regex, suggestion
$patterns = @(
    # Destructive file ops (critical/high)
    @("destructive_file_ops", "critical", "rm\s+-r\s*f?\s*/(\s|$)", "Use targeted paths or mv to back up first"),
    @("destructive_file_ops", "critical", "rm\s+-r\s*f?\s*~", "Never delete home directory recursively"),
    @("destructive_file_ops", "critical", "rm\s+-r\s*f?\s*\.(\s|$)", "Use targeted paths instead of current directory"),
    @("destructive_file_ops", "high", "rm\s+.*\.env", "Use mv to back up .env files first"),
    @("destructive_file_ops", "high", "rm\s+.*\.git", "Never delete .git directory"),
    # Destructive git ops (critical/high)
    @("destructive_git_ops", "critical", "git\s+push\s+--force\s+(origin\s+)?(main|master)", "Use --force-with-lease or push to feature branch"),
    @("destructive_git_ops", "high", "git\s+reset\s+--hard", "Use git stash or create backup branch first"),
    @("destructive_git_ops", "high", "git\s+clean\s+-[a-z]*f[a-z]*d", "Use --dry-run first: git clean -fdn"),
    # Database destruction (critical/high)
    @("database_destruction", "critical", "DROP\s+DATABASE", "Use migrations and backups instead"),
    @("database_destruction", "critical", "DROP\s+TABLE", "Use migrations for schema changes"),
    @("database_destruction", "high", "TRUNCATE\s+", "Use DELETE with WHERE clause"),
    @("database_destruction", "high", "DELETE\s+FROM\s+[a-zA-Z_]+\s*;", "Add a WHERE clause to limit deletion scope"),
    # Permission abuse (high)
    @("permission_abuse", "high", "chmod\s+([0-9]*7[0-9]*7[0-9]*7|777)", "Use 755 for dirs, 644 for files"),
    @("permission_abuse", "high", "chmod\s+-R\s+777", "Use least-privilege permissions"),
    # Network exfiltration (critical/high)
    @("network_exfiltration", "critical", "curl\s+.*\|\s*bash", "Download first, review, then execute"),
    @("network_exfiltration", "critical", "wget\s+.*\|\s*sh", "Download first, review, then execute"),
    @("network_exfiltration", "high", "curl\s+--data\s+@", "Review data before uploading"),
    # System danger (high)
    @("system_danger", "high", "sudo\s+", "Avoid elevated privileges; use least-privilege approach"),
    @("system_danger", "high", "npm\s+publish", "Use --dry-run first: npm publish --dry-run")
)

$threats = @()

# Repository policy: agents must never run git commands. Block all shell git usage.
if ($isCommandTool -and ($toolInput -match "\bgit(\.exe)?\s+")) {
    $threats += @{
        category = "git_operations_blocked"
        severity = "critical"
        match = "git"
        suggestion = "Git commands are disabled for agents in this repository; ask the user to run git manually."
    }
}

foreach ($p in $patterns) {
    if ($scanText -match $p[2]) {
        $threats += @{ category = $p[0]; severity = $p[1]; match = $Matches[0]; suggestion = $p[3] }
    }
}

if ($threats.Count -gt 0) {
    $logEntry = @{
        timestamp = $timestamp; event = "threats_detected"; mode = $GuardMode
        tool = $toolName; threat_count = $threats.Count; threats = $threats
    } | ConvertTo-Json -Compress
    Add-Content -Path "$LogDir\guard.log" -Value $logEntry

    if ($GuardMode -eq "block") {
        $reason = "Tool Guardian: $($threats.Count) threat(s) detected"
        @{ hookSpecificOutput = @{ hookEventName = "PreToolUse"; permissionDecision = "deny"; permissionDecisionReason = $reason } } | ConvertTo-Json -Compress
        exit 2
    }
    else {
        @{ systemMessage = "Tool Guardian: $($threats.Count) threat(s) detected (warn mode)" } | ConvertTo-Json -Compress
        exit 0
    }
}
else {
    $logEntry = @{ timestamp = $timestamp; event = "guard_passed"; mode = $GuardMode; tool = $toolName } | ConvertTo-Json -Compress
    Add-Content -Path "$LogDir\guard.log" -Value $logEntry
    exit 0
}
