"""Small entrypoint script used for local runs and PyInstaller builds.

This keeps the executable entrypoint separate from the web framework
module and keeps the app import path stable.
"""

from __future__ import annotations

import os

import uvicorn


def main() -> None:
    # Default to localhost for safety; override with VOICE_HOST to bind elsewhere
    host = os.getenv("VOICE_HOST", "127.0.0.1")
    port = int(os.getenv("VOICE_PORT", "8000"))
    reload = os.getenv("VOICE_RELOAD", "false").lower() == "true"
    uvicorn.run("voice.interaction.main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    main()
