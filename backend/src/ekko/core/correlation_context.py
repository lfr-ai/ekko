"""Execution-context helpers for request correlation identifiers.

A :class:`~contextvars.ContextVar` carries the request correlation id across the
async call stack so log records can be enriched with it automatically, without
threading the value through every function signature.
"""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

_request_id_var = ContextVar[str | None]("ekko_request_id", default=None)


def get_request_id() -> str | None:
    """Look up the request correlation id bound in the current context.

    Returns:
        str | None: Correlation id, or ``None`` when no request is bound.
    """
    return _request_id_var.get()


@contextmanager
def bind_request_id(request_id: str) -> Iterator[None]:
    """Bind a request correlation id for the duration of the context.

    Args:
        request_id (str): Correlation id to bind to the current context.

    Yields:
        None: Control while the correlation id is bound.
    """
    token = _request_id_var.set(request_id)
    try:
        yield
    finally:
        _request_id_var.reset(token)
