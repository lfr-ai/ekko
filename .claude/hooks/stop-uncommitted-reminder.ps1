# Uncommitted Files Reminder — Stop hook (Windows)
# Outputs a systemMessage JSON reminder when uncommitted files exist.
param()

$status = git status --porcelain 2>$null
if (-not $status) { exit 0 }

$count = ($status | Measure-Object -Line).Lines
$json = @{
    systemMessage = "Reminder: $count uncommitted file(s) in working tree."
} | ConvertTo-Json -Compress

Write-Output $json
exit 0
