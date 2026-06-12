"""Runtime configuration resolution.

Resolves the active environment from the EKKO_ENVIRONMENT variable and exposes
shared runtime constants used during settings construction.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Final

from ekko import APP_NAME
from ekko.config.enums import Environment

_ROOT_PARENT_LEVEL = 3
ROOT_DIR: Final[Path] = Path(__file__).resolve().parents[_ROOT_PARENT_LEVEL]


def _resolve_runtime_environment() -> Environment:
    """Resolve runtime environment from EKKO_ENVIRONMENT env var.

    Returns:
        Environment: Resolved environment enum. Defaults to LOCAL.
    """
    env_name = os.getenv("EKKO_ENVIRONMENT", Environment.LOCAL.value)
    try:
        return Environment(env_name.lower())
    except ValueError:
        return Environment.LOCAL


ENV: Final[Environment] = _resolve_runtime_environment()
APP: Final[str] = APP_NAME
