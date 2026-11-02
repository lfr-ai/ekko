"""Small entrypoint script used for local runs and PyInstaller builds.

This keeps the executable entrypoint separate from the web framework
module and keeps the app import path stable.
"""

from __future__ import annotations

import os
import sys
import webbrowser

import uvicorn

_HOST_ENV_VAR = "EKKO_HOST"
_PORT_ENV_VAR = "EKKO_PORT"
_RELOAD_ENV_VAR = "EKKO_RELOAD"
_OPEN_BROWSER_ENV_VAR = "EKKO_OPEN_BROWSER"
_DEFAULT_HOST = "127.0.0.1"
_DEFAULT_PORT = "8000"
_DEFAULT_RELOAD_FLAG = "false"
_DEFAULT_OPEN_BROWSER_FLAG = "true"


def main() -> None:
    """Launch the Ekko application entrypoint."""
    frozen = getattr(sys, "frozen", False)

    if frozen:
        os.environ.setdefault("EKKO_ENVIRONMENT", "local")

    host = os.getenv(_HOST_ENV_VAR, _DEFAULT_HOST)
    port = int(os.getenv(_PORT_ENV_VAR, _DEFAULT_PORT))
    reload = not frozen and os.getenv(_RELOAD_ENV_VAR, _DEFAULT_RELOAD_FLAG).lower() == "true"
    open_browser = os.getenv(_OPEN_BROWSER_ENV_VAR, _DEFAULT_OPEN_BROWSER_FLAG).lower() == "true"

    if frozen and open_browser:
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
