import asyncio
import msgpack
from utils.logger import Logger

class SyncNetChannel(asyncio.Protocol):

    def __init__(self,
                    transport=None,
                    server=None,
                    serializer=None,
                    deserializer=None):
        self.transport = transport
        self.server = server
        if self.transport:
            self.address = transport.get_extra_info('peername')
        self.sendqueue = []
        self._serializer = serializer or msgpack.packb
        self._deserializer = deserializer
        

    def connection_made(self, transport):
        if self.transport is None:
            self.transport = transport

        if not hasattr(self, 'address'):
            self.address = self.transport.get_extra_info('peername')
    
    def data_received(self, data):
        unpacker = msgpack.Unpacker()
        has_deserializer = True
        if self._deserializer is None:
            unpacker.feed(data)
            has_deserializer = False
            
        if has_deserializer:
            decoded = self._deserializer(data)
            if isinstance(decoded, dict) and decoded.get('action'):
                [getattr(self, method)(decoded) for method in ('syncnet_'+decoded.get('action'), 'handler') if hasattr(self, method)]
        else:
            for message in unpacker:
                if isinstance(message, dict) and message.get('action'):
                    [getattr(self, method)(message) for method in ('syncnet_'+message.get('action'), 'handler') if hasattr(self, method)]
    
    def send(self, data):
        decoded = self._serializer(data)
        self.sendqueue.append(decoded)
    
    def update(self):
        if self.transport is None or self.transport.is_closing():
            return
        
        for data in self.sendqueue:
            self.transport.write(data)
        self.sendqueue = []
    
    def connection_lost(self, exc):
        if hasattr(self, 'close'):
            Logger.i("I am triggered")
            self.close()
