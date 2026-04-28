"""Simple CLI to send a payload to the TCP queue server.

Usage: python -m voice.cli.send_tcp --host 127.0.0.1 --port 8800 --queue my-queue --file payload.bin
Or echo text | python -m voice.cli.send_tcp --queue my-queue
"""

from __future__ import annotations

import argparse
import asyncio
import sys


async def send(host: str, port: int, queue: str, data: bytes) -> None:
    reader, writer = await asyncio.open_connection(host, port)
    try:
        writer.write(queue.encode("utf-8") + b"\n")
        writer.write(data)
        await writer.drain()
    finally:
        writer.close()
        await writer.wait_closed()


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8800)
    parser.add_argument("--queue", required=True)
    parser.add_argument("--file", help="File to send; if omitted reads stdin")
    args = parser.parse_args(argv)

    if args.file:
        with open(args.file, "rb") as f:
            data = f.read()
    else:
        data = sys.stdin.buffer.read()

    asyncio.run(send(args.host, args.port, args.queue, data))


if __name__ == "__main__":
    main()
