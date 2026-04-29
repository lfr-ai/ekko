from ekko.infrastructure.concurrency.queue_manager import QueueManager


def test_queue_create_and_put_get():
    qm = QueueManager()
    qm.create_queue("test")
    qm.put_in_queue("test", 123)
    val = qm.get_from_queue("test", timeout=1)
    assert val == 123
    qm.task_done("test")
