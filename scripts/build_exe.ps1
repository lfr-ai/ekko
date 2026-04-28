Param()
Set-StrictMode -Version Latest

Write-Host "Building standalone executable with PyInstaller..."

if (Get-Command uv -ErrorAction SilentlyContinue) {
    uv run pyinstaller --clean --onefile --name voice-bot-app src/voice/cli/run_app.py
} else {
    pyinstaller --clean --onefile --name voice-bot-app src/voice/cli/run_app.py
}

Write-Host "Build complete: dist/voice-bot-app.exe"
param(
    [string]$Entry = 'src\voice\interaction\main.py',
    [string]$Name = 'voice-bot'
)

Write-Host "Building $Name from $Entry"

Remove-Item -Recurse -Force build, dist, "$Name.spec" -ErrorAction SilentlyContinue

pyinstaller --noconfirm --clean --onefile --name $Name $Entry

Write-Host "Build complete. Executable is in ./dist"
