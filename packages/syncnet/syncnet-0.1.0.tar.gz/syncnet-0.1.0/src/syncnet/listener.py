from .endpoint import SyncNetEndPoint
import asyncio
import sys

class SyncNetListener:
    
    _connection = SyncNetEndPoint()

    @classmethod
    def update_network(cls):
        cls._connection.update()

    @classmethod
    async def connect(cls, address=None):
        if address:
            cls._connection.address = address

        try:
            if cls._connection._is_running:
                return 
        
            loop = asyncio.get_running_loop()
            cls.transport, cls.protocol = await loop.create_connection(
                lambda: cls._connection,
                cls._connection.address[0],
                cls._connection.address[1]
            )
            cls._connection._is_running = True
        except ConnectionRefusedError as err:
            sys.stderr.write(err.strerror + "\n")
            exit(1)

    def update(self):
        for data in self._connection.queue:
            if isinstance(data, dict) and data.get('action'):
                [getattr(self, method)(data) for method in ('syncnet_'+data.get('action'), 'handler') if hasattr(self, method)]
        self.update_network()

    def send(self, data):
        self._connection.send(data)

    @property
    def is_running(self):
        return self._connection._is_running