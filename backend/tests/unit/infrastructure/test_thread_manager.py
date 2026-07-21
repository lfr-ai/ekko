import time

from ekko.infrastructure.concurrency.thread_manager import ThreadManager


def test_start_and_stop_thread():
    tm = ThreadManager()

    result = {"ran": False}

    def worker(stop_event):
        # simple loop that stops when stop_event is set
        while not stop_event.is_set():
            time.sleep(0.01)
        result["ran"] = True

    tm.start_thread(worker, tm.stop_event)
    time.sleep(0.05)
    tm.stop_all_threads()
    # give threads a short moment to join
    time.sleep(0.05)
    assert result["ran"] is True
