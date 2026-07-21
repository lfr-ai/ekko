import asyncio
import socket
import threading
import time

from ekko.infrastructure.concurrency.queue_manager import QueueManager
from ekko.infrastructure.concurrency.tcp_queue import TCPQueueServer


def tcp_server(host: str, port: int, qm: QueueManager, queue_name: str, stop_event):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(1)
    s.settimeout(0.5)
    try:
        while not stop_event.is_set():
            try:
                conn, _ = s.accept()
            except Exception:  # noqa: S112
                continue
            with conn:
                data = conn.recv(1024)
                if data:
                    qm.put_in_queue(queue_name, data)
    finally:
        s.close()


def test_tcp_to_queue_roundtrip():
    host = "127.0.0.1"
    port = 55055
    qm = QueueManager()
    queue_name = "test-queue"
    qm.create_queue(queue_name)

    stop_event = threading.Event()
    t = threading.Thread(target=tcp_server, args=(host, port, qm, queue_name, stop_event), daemon=True)
    t.start()

    time.sleep(0.2)

    # client sends bytes
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    payload = b"hello-bytes"
    client.sendall(payload)
    client.close()

    # wait for server to process
    time.sleep(0.2)

    received = qm.get_from_queue(queue_name, timeout=1)
    assert received == payload

    stop_event.set()
    t.join(timeout=1)


def test_tcp_queue_end_to_end():
    async def run():
        qm = QueueManager()
        server = TCPQueueServer(host="127.0.0.1", port=8800, qm=qm)
        await server.start()

        _, writer = await asyncio.open_connection("127.0.0.1", 8800)
        # send queue name and payload
        writer.write(b"test-queue\n")
        writer.write(b"hello-from-tcp")
        await writer.drain()
        writer.close()
        await writer.wait_closed()

        # give server a short moment to process
        await asyncio.sleep(0.05)

        val = qm.get_from_queue("test-queue", timeout=1)
        assert val == b"hello-from-tcp"

        await server.stop()

    asyncio.run(run())
