# Placeholder: will handle retry logic, file-based queues, etc.

class EmailQueue:
    def __init__(self):
        self.queue = []

    def add(self, email_data):
        self.queue.append(email_data)

    def process(self):
        for job in self.queue:
            pass  # Retry logic to be implemented