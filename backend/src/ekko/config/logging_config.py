"""Logging configuration helpers for the Ekko application.

Keep a small, test-friendly ``configure_logging`` helper that can be called
from application startup code. Avoid side-effects at import time so tests
can import modules without automatically configuring global logging state.
"""

from __future__ import annotations

import logging
import os
from logging.config import dictConfig

from ekko.config.settings import get_settings


def configure_logging(level: str | None = None) -> None:
    """Configure structured logging for the application.

    If logging is already configured (handlers present on the root logger) this
    function returns immediately. ``level`` may be provided or defaults to
    ``EKKO_LOG_LEVEL`` env var or the settings' log level.
    """
    if logging.getLogger().handlers:
        return

    settings = get_settings()
    level = level or os.getenv("EKKO_LOG_LEVEL") or logging.getLevelName(settings.log_level)

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
    if getattr(settings, "sentry_dsn", None):
        try:
            import sentry_sdk

            sentry_sdk.init(dsn=settings.sentry_dsn)
        except Exception:
            logging.getLogger(__name__).warning("Failed to initialize Sentry SDK")
