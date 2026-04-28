"""Simple asyncio TCP queue server for IPC between processes.

Protocol: client connects, sends a single line queue name (utf-8, terminated by LF),
then sends payload bytes (raw) until connection close. The server will push the
payload into the named queue in the provided QueueManager (creating the queue if missing).
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

from voice.managers.queue_manager import QueueManager

logger = logging.getLogger(__name__)


class TCPQueueServer:
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 7000,
        qm: Optional[QueueManager] = None,
    ) -> None:
        self.host = host
        self.port = port
        self.qm = qm or QueueManager()
        self.server: Optional[asyncio.AbstractServer] = None

    async def _handle(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            # read queue name line
            line = await reader.readline()
            if not line:
                return
            queue_name = line.decode("utf-8").strip()
            # ensure queue exists
            if queue_name not in self.qm.queues:
                self.qm.create_queue(queue_name)

            # read remaining bytes until EOF
            payload = await reader.read()
            if payload:
                self.qm.put_in_queue(queue_name, payload)
        except Exception as e:
            # avoid failing the server on client errors
            logger.debug("TCPQueueServer client handler error: %s", e)
            return
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                logger.debug("Failed to close writer in TCPQueueServer: %s", e)

    async def start(self) -> None:
        """Start the TCP server (non-blocking)."""
        self.server = await asyncio.start_server(self._handle, self.host, self.port)

    async def stop(self) -> None:
        """Stop the TCP server and close listeners."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()

    def get_queue_manager(self) -> QueueManager:
        return self.qm
