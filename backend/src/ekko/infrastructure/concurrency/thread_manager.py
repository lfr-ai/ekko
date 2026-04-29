"""Daemon thread manager with cooperative shutdown."""

from __future__ import annotations

from threading import Event, Thread
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable


class ThreadManager:
    """Manager for daemon threads with a shared stop event."""

    def __init__(self) -> None:
        self.threads: list[Thread] = []
        self.stop_event = Event()

    def start_thread(
        self,
        target: Callable[..., None],
        /,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Start a new daemon thread and track it."""
        thread = Thread(target=target, args=args, kwargs=kwargs, daemon=True)
        self.threads.append(thread)
        thread.start()

    def stop_all_threads(self) -> None:
        """Set the stop event and wait for all threads to finish."""
        self.stop_event.set()
        self._wait_for_threads()

    def _wait_for_threads(self, timeout: float | None = None) -> None:
        """Wait for all living threads to finish."""
        for thread in self.threads:
            if thread and thread.is_alive():
                thread.join(timeout)
