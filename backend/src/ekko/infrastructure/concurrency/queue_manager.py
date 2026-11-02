"""Thread-safe FIFO queue manager."""

from __future__ import annotations

from queue import Queue
from typing import final


@final
class QueueManager:
    """Manager for named, thread-safe FIFO queues."""

    def __init__(self):  # noqa: ANN204 - project convention omits __init__ return annotations.
        self.queues: dict[str, Queue[object]] = {}

    def create_queue(self, name: str) -> None:
        """Create a new queue with the given name.

        Args:
            name (str): Unique identifier for the queue.

        Raises:
            TypeError: If *name* is not a string.
            ValueError: If a queue with *name* already exists.
        """
        if not isinstance(name, str):
            msg = "Queue name must be a string."
            raise TypeError(msg)
        if name in self.queues:
            msg = f"Queue '{name}' already exists."
            raise ValueError(msg)
        self.queues[name] = Queue()

    def get_queue(self, name: str) -> Queue[object]:
        """Look up the queue associated with *name*.

        Args:
            name (str): Queue identifier to look up.

        Returns:
            Queue[object]: Named queue instance.

        Raises:
            KeyError: If *name* does not exist.
        """
        try:
            return self.queues[name]
        except KeyError as exc:
            msg = f"Queue '{name}' does not exist."
            raise KeyError(msg) from exc

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

        Args:
            name (str): Queue identifier to remove.

        Raises:
            KeyError: If *name* does not exist.
        """
        if name in self.queues:
            del self.queues[name]
        else:
            msg = f"Queue '{name}' does not exist."
            raise KeyError(msg)
