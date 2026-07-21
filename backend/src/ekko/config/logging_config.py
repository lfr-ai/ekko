"""Application logging configuration with JSON file output and console rendering.

Configures Python stdlib logging with:
- JSON output for file handlers (production/machine-readable)
- Human-readable console output for development
- Weekly file rotation with configurable backup count
- Suppression of noisy third-party loggers
"""

from __future__ import annotations

import json
import logging
import os
from datetime import UTC, datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from ekko import APP_NAME
from ekko.config.settings import get_settings

_LOG_FILENAME = "app.log"
_DEFAULT_BACKUP_COUNT = 10
_CONSOLE_FORMAT = "%(asctime)s %(levelname)-8s %(name)s | %(message)s"
_CONSOLE_DATE_FORMAT = "%H:%M:%S"

_SUPPRESSED_LOGGERS = frozenset(
    {
        "httpcore",
        "httpx",
        "hpack",
        "websockets",
        "watchfiles",
    }
)


class _JSONFormatter(logging.Formatter):
    """JSON log formatter for machine-readable file output."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as a single-line JSON object."""
        entry: dict[str, object] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info and record.exc_info[0] is not None:
            entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(entry, default=str, ensure_ascii=False)


def configure_logging(level: str | None = None) -> None:
    """Configure structured logging for the application.

    Sets up JSON file output with weekly rotation plus human-readable console.
    If logging is already configured (handlers present) this returns immediately.
    """
    if logging.getLogger().handlers:
        return

    settings = get_settings()
    level = level or os.getenv("EKKO_LOG_LEVEL") or str(settings.log_level)
    numeric_level = getattr(logging, level.upper(), logging.INFO) if isinstance(level, str) else level

    # Ensure logs directory exists
    root_dir_value = getattr(settings, "root_dir", None)
    logs_dir = Path(str(root_dir_value)) / "logs" if root_dir_value is not None else Path("logs")
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Reset root logger
    root = logging.getLogger()
    root.setLevel(numeric_level)
    root.handlers.clear()

    # File handler: weekly-rotated JSON
    file_handler = TimedRotatingFileHandler(
        filename=logs_dir / _LOG_FILENAME,
        when="W0",
        interval=1,
        backupCount=_DEFAULT_BACKUP_COUNT,
        encoding="utf-8",
        delay=True,
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(_JSONFormatter())
    root.addHandler(file_handler)

    # Console handler: human-readable
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(logging.Formatter(fmt=_CONSOLE_FORMAT, datefmt=_CONSOLE_DATE_FORMAT))
    root.addHandler(console_handler)

    # Suppress noisy third-party loggers
    for name in _SUPPRESSED_LOGGERS:
        logging.getLogger(name).setLevel(logging.WARNING)

    # Optional: initialize Sentry if configured
    if getattr(settings, "sentry_dsn", None):
        try:
            import sentry_sdk

            sentry_sdk.init(dsn=settings.sentry_dsn)
        except Exception:
            logging.getLogger(__name__).warning("Failed to initialize Sentry SDK")

    logging.getLogger(APP_NAME).info("logging_configured")
