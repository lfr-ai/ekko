"""Thread-safe FIFO queue manager."""

from __future__ import annotations

from queue import Queue
from typing import Any


class QueueManager:
    """Manager for named, thread-safe FIFO queues."""

    def __init__(self) -> None:
        self.queues: dict[str, Queue[Any]] = {}

    def create_queue(self, name: str) -> None:
        """Create a new queue with the given name.

        Raises:
            TypeError: If *name* is not a string.
            ValueError: If a queue with *name* already exists.
        """
        if not isinstance(name, str):
            raise TypeError("Queue name must be a string.")
        if name in self.queues:
            raise ValueError(f"Queue '{name}' already exists.")
        self.queues[name] = Queue()

    def get_queue(self, name: str) -> Queue[Any]:
        """Return the queue associated with *name*.

        Raises:
            KeyError: If *name* does not exist.
        """
        try:
            return self.queues[name]
        except KeyError as err:
            raise KeyError(f"Queue '{name}' does not exist.") from err

    def put_in_queue(self, name: str, item: object) -> None:
        """Put *item* into the named queue."""
        self.get_queue(name).put(item)

    def get_from_queue(self, name: str, timeout: float | int | None = None) -> object:
        """Get an item from the named queue."""
        return self.get_queue(name).get(timeout=timeout)

    def task_done(self, name: str) -> None:
        """Signal that a task from the named queue is complete."""
        self.get_queue(name).task_done()

    def join_queue(self, name: str) -> None:
        """Block until all items in the named queue have been processed."""
        self.get_queue(name).join()

    def remove_queue(self, name: str) -> None:
        """Remove a named queue.

        Raises:
            KeyError: If *name* does not exist.
        """
        if name in self.queues:
            del self.queues[name]
        else:
            raise KeyError(f"Queue '{name}' does not exist.")
