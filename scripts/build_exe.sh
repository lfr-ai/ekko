#!/usr/bin/env bash
set -euo pipefail

echo "Building standalone executable with PyInstaller..."

# Use the project's task runner if available; fall back to pyinstaller directly
if command -v uv >/dev/null 2>&1; then
  uv run pyinstaller --clean --onefile --name voice-bot-app src/voice/cli/run_app.py
else
  pyinstaller --clean --onefile --name voice-bot-app src/voice/cli/run_app.py
fi

echo "Build complete: dist/voice-bot-app"
#!/usr/bin/env bash
set -euo pipefail

# Build a single-file executable using PyInstaller.
# Note: Run this on the target platform (PyInstaller is not a cross-compiler).
# Ensure dev dependencies are installed: pdm add -d pyinstaller OR uv tool install pyinstaller.

APP_NAME=voice-bot
ENTRY=src/voice/interaction/main.py
DIST_DIR=dist

echo "Building ${APP_NAME} from ${ENTRY}"

# Clean previous build artifacts
rm -rf build ${DIST_DIR} ${APP_NAME}.spec

pyinstaller --noconfirm --clean --onefile --name ${APP_NAME} ${ENTRY}

echo "Build complete. Executable located in ${DIST_DIR}/"
