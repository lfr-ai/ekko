"""Logging configuration helpers for the voice application.

Keep a small, test-friendly ``configure_logging`` helper that can be called
from application startup code. Avoid side-effects at import time so tests
can import modules without automatically configuring global logging state.
"""

from __future__ import annotations

import logging
import os
from logging.config import dictConfig
from typing import Optional

from voice.config.settings import SETTINGS


def configure_logging(level: Optional[str] = None) -> None:
    """Configure structured logging for the application.

    If logging is already configured (handlers present on the root logger) this
    function returns immediately. ``level`` may be provided or defaults to
    ``VOICE_LOG_LEVEL`` env var or the settings' log level.
    """
    if logging.getLogger().handlers:
        return

    level = level or os.getenv("VOICE_LOG_LEVEL") or logging.getLevelName(SETTINGS.log_level)

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "logging.Formatter",
                "fmt": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
            }
        },
        "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "default", "level": level}},
        "root": {"handlers": ["console"], "level": level},
    }

    dictConfig(config)

    # Optional: initialize Sentry if configured
    if getattr(SETTINGS, "sentry_dsn", None):
        try:
            import sentry_sdk

            sentry_sdk.init(dsn=SETTINGS.sentry_dsn)
        except Exception:
            logging.getLogger(__name__).warning("Failed to initialize Sentry SDK")
