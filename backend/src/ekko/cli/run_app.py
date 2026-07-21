"""Small entrypoint script used for local runs and PyInstaller builds.

This keeps the executable entrypoint separate from the web framework
module and keeps the app import path stable.
"""

from __future__ import annotations

import os
import sys
import webbrowser

import uvicorn


def main() -> None:
    frozen = getattr(sys, "frozen", False)

    if frozen:
        os.environ.setdefault("EKKO_ENVIRONMENT", "local")

    host = os.getenv("EKKO_HOST", "127.0.0.1")
    port = int(os.getenv("EKKO_PORT", "8000"))
    reload = not frozen and os.getenv("EKKO_RELOAD", "false").lower() == "true"

    if frozen:
        webbrowser.open(f"http://{host}:{port}")

    uvicorn.run(
        "ekko.composition.app_factory:create_app",
        factory=True,
        host=host,
        port=port,
        reload=reload,
    )


if __name__ == "__main__":
    main()
