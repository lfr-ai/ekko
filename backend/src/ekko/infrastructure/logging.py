"""Structured logging foundation.

Configures the stdlib :mod:`logging` root logger with a rotating file sink and
an optional console sink. A custom formatter appends structured ``extra`` fields
to each line as ``key=value`` tokens, and an optional filter injects contextual
values (such as the request correlation id) at emit time.

Callers pass a short human-readable message and attach structured data via the
``extra`` mapping, for example::

    _logger.info("Remote document loaded", extra={"size_bytes": 2048})
"""

from __future__ import annotations

import logging
import logging.handlers
import os
from multiprocessing import current_process
from typing import TYPE_CHECKING, final, override

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

_FORMAT = "{asctime} {levelname} {name} {module}.{funcName}:{lineno} - {message}"

# Attribute names present on every LogRecord; anything else is a caller "extra".
_STANDARD_LOG_RECORD_FIELDS = frozenset(logging.makeLogRecord({}).__dict__) | {
    "message",
    "asctime",
}


def resolve_process_log_filename(base_filename: str) -> str:
    """Build a process-safe log filename for main and worker processes.

    Worker processes receive a pid-scoped suffix so multiple workers never write
    to the same rotating file concurrently.

    Args:
        base_filename (str): Base log filename used by the main process.

    Returns:
        str: Log filename to use for the current process.
    """
    if current_process().name == "MainProcess":
        return base_filename
    return f"{base_filename}.{os.getpid()}.log"


@final
class ContextInjectingFilter(logging.Filter):
    """Inject contextual field values into log records at emit time."""

    def __init__(self, field_providers: tuple[tuple[str, Callable[[], str | None]], ...]):
        """Store the field providers used to enrich records.

        Args:
            field_providers (tuple[tuple[str, Callable[[], str | None]], ...]):
                Pairs of field name and a lazy provider returning its value.
        """
        super().__init__()
        self._field_providers = field_providers

    @override
    def filter(self, record: logging.LogRecord) -> bool:
        """Attach available provider values to the record.

        Args:
            record (logging.LogRecord): Record to enrich.

        Returns:
            bool: Always ``True`` so the record is never dropped.
        """
        for field_name, field_provider in self._field_providers:
            if field_value := field_provider():
                setattr(record, field_name, field_value)
        return True


class _ExtraFormatter(logging.Formatter):
    """Append structured ``extra`` record fields to the base log line."""

    def __init__(self, prioritized_fields: tuple[str, ...] | None = None):
        """Store optional field-priority ordering.

        Args:
            prioritized_fields (tuple[str, ...] | None): Fields to render first,
                in the given order, ahead of any remaining extras.
        """
        super().__init__(fmt=_FORMAT, style="{")
        self._prioritized_fields = prioritized_fields or ()
        self._prioritized_field_set = frozenset(self._prioritized_fields)

    @override
    def format(self, record: logging.LogRecord) -> str:
        """Format the base line and append any structured extra fields.

        Args:
            record (logging.LogRecord): Record to render.

        Returns:
            str: Rendered log line with ``key=value`` extras appended.
        """
        base_line = super().format(record)

        extra_fields = {
            field_name: field_value
            for field_name, field_value in record.__dict__.items()
            if field_name not in _STANDARD_LOG_RECORD_FIELDS
        }
        if not extra_fields:
            return base_line

        if not self._prioritized_fields:
            ordered_field_names = list(extra_fields)
        else:
            ordered_field_names = [name for name in self._prioritized_fields if name in extra_fields]
            ordered_field_names.extend(name for name in extra_fields if name not in self._prioritized_field_set)

        rendered_extras = " ".join(f"{name}={extra_fields[name]}" for name in ordered_field_names)
        return f"{base_line} | {rendered_extras}"


def _prepare_handler(
    handler: logging.Handler,
    *,
    level: int,
    formatter: logging.Formatter,
    record_filter: logging.Filter | None,
) -> logging.Handler:
    """Apply level, formatter, and optional filter to a handler.

    Args:
        handler (logging.Handler): Handler to configure.
        level (int): Minimum severity the handler emits.
        formatter (logging.Formatter): Formatter applied to records.
        record_filter (logging.Filter | None): Optional enrichment filter.

    Returns:
        logging.Handler: Configured handler.
    """
    handler.setLevel(level)
    handler.setFormatter(formatter)
    if record_filter:
        handler.addFilter(record_filter)
    return handler


def configure_logging(
    *,
    log_dir_path: Path,
    log_filename: str,
    log_level: int = logging.INFO,
    to_console: bool = True,
    record_filter: logging.Filter | None = None,
    prioritized_fields: tuple[str, ...] | None = None,
    noisy_loggers: tuple[str, ...] | None = None,
) -> None:
    """Configure the root logger with rotating file and optional console sinks.

    Args:
        log_dir_path (Path): Directory for the log file; created if absent.
        log_filename (str): Log filename for the current process.
        log_level (int): Minimum severity emitted by the root logger.
        to_console (bool): Whether to mirror logs to ``stderr``.
        record_filter (logging.Filter | None): Optional enrichment filter applied
            to every handler.
        prioritized_fields (tuple[str, ...] | None): Extra fields to render first.
        noisy_loggers (tuple[str, ...] | None): Third-party logger names forced to
            ``WARNING`` so they do not flood the output.
    """
    log_dir_path.mkdir(parents=True, exist_ok=True)
    formatter = _ExtraFormatter(prioritized_fields)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)

    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_dir_path / log_filename,
        when="W0",
        backupCount=10,
        encoding="utf-8",
        delay=True,
    )
    root_logger.addHandler(
        _prepare_handler(file_handler, level=log_level, formatter=formatter, record_filter=record_filter)
    )

    if to_console:
        root_logger.addHandler(
            _prepare_handler(
                logging.StreamHandler(),
                level=log_level,
                formatter=formatter,
                record_filter=record_filter,
            )
        )

    for logger_name in noisy_loggers or ():
        noisy_logger = logging.getLogger(logger_name)
        noisy_logger.handlers.clear()
        noisy_logger.setLevel(logging.WARNING)
        noisy_logger.propagate = True
