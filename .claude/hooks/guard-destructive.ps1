# Guard Destructive Commands — PreToolUse hook (Windows)
# Blocks rm -rf /, git push --force, DROP DATABASE, curl|bash
param()

$input_json = $input | Out-String
if ([string]::IsNullOrWhiteSpace($input_json)) { exit 0 }

try {
    $parsed = $input_json | ConvertFrom-Json
    $command = $parsed.tool_input.command
} catch {
    exit 0
}

if ([string]::IsNullOrWhiteSpace($command)) { exit 0 }

$destructivePatterns = @(
    'rm\s+-r\s*f?\s*/',
    'git\s+push\s+--force',
    'git\s+reset\s+--hard',
    'git\s+clean\s+-fd',
    'DROP\s+(DATABASE|TABLE)',
    'curl\s+.*\|\s*(ba)?sh',
    'wget\s+.*\|\s*(ba)?sh',
    'chmod\s+777',
    'mkfs\.',
    ':>\s*/'
)

$combinedPattern = $destructivePatterns -join '|'

if ($command -match $combinedPattern) {
    $result = @{
        hookSpecificOutput = @{
            hookEventName = "PreToolUse"
            permissionDecision = "deny"
            permissionDecisionReason = "Blocked by guard-destructive hook: potentially destructive command detected"
        }
    } | ConvertTo-Json -Compress
    Write-Output $result
    exit 2
}

exit 0
