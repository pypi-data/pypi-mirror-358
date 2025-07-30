from .channel import SyncNetChannel

class SyncNetEndPoint(SyncNetChannel):

    def __init__(self, address=('127.0.0.1', 5000)):
        super().__init__()
        self._queue = []
        self.address = address
        self._is_running = False

    def handler(self, data):
        self._queue.append(data)

    def update(self):
        super().update()
        self._queue = []

    def close(self):
        self._is_running = False
        self._queue.append({"action": "disconnected"})
        self.update()
        self.transport.close()

    @property
    def queue(self):
        return self._queue

    @property
    def is_running(self):
        return self._is_running
