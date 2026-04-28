param(
    [string]$Entry = 'src\voice\interaction\main.py',
    [string]$Name = 'voice-bot'
)

Write-Host "Building $Name from $Entry"

Remove-Item -Recurse -Force build, dist, "$Name.spec" -ErrorAction SilentlyContinue

pyinstaller --noconfirm --clean --onefile --name $Name $Entry

Write-Host "Build complete. Executable is in ./dist"
