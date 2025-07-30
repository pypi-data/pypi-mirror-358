from openmailer.queue import EmailQueue

def test_queue_add_and_process_stub():
    queue = EmailQueue()
    queue.add({"to": "example@example", "subject": "Queued"})
    assert len(queue.queue) == 1

    # Processing not yet implemented
    queue.process()