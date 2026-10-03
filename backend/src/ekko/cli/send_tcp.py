"""Simple CLI to send a payload to the TCP queue server.

Usage: python -m ekko.cli.send_tcp --host 127.0.0.1 --port 8800 --queue my-queue --file payload.bin
Or echo text | python -m ekko.cli.send_tcp --queue my-queue
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

_DEFAULT_HOST = "127.0.0.1"
_DEFAULT_PORT = 8800


async def send(host: str, port: int, queue: str, data: bytes) -> None:
    """Send a payload to the TCP queue server."""
    _reader, writer = await asyncio.open_connection(host, port)
    try:
        writer.write(queue.encode("utf-8") + b"\n")
        writer.write(data)
        await writer.drain()
    finally:
        writer.close()
        await writer.wait_closed()


def main(argv: list[str] | None = None) -> None:
    """Parse arguments and send a payload to the queue server."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=_DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=_DEFAULT_PORT)
    parser.add_argument("--queue", required=True)
    parser.add_argument("--file", help="File to send; if omitted reads stdin")
    args = parser.parse_args(argv)

    if args.file:
        with Path(args.file).open("rb") as f:
            data = f.read()
    else:
        data = sys.stdin.buffer.read()

    asyncio.run(send(args.host, args.port, args.queue, data))


if __name__ == "__main__":
    main()
