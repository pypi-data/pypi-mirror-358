import asyncio
import socket
import msgpack
from typing import Optional, Type

class SyncNetServer(asyncio.Protocol):

    def __init__(self, channelClass:Type=None,  address =('127.0.0.1', 5000), listeners=5):
        self.channelClass = channelClass
        self.address = address
        self.listeners = listeners
        self.channels = []
        self._server: Optional[asyncio.Server] = None
        self._server_task: Optional[asyncio.Task] = None
        self._is_running = False
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        channel = self.channelClass(transport, self)
        self.channels.append(channel)
        if hasattr(self, 'syncnet_connected'):
            self.syncnet_connected(channel)
        
        channel.send({"action": "connected"})
    
    def connection_lost(self, exc):
        return super().connection_lost(exc)
    
    def data_received(self, data):
        unpacker = msgpack.Unpacker()
        unpacker.feed(data)
        for message in unpacker:
            if isinstance(message, dict):
                for ch in self.channels[:]:
                    if message.get('action') and hasattr(ch, 'syncnet_' + message['action']):
                        getattr(ch, 'syncnet_'+message['action'])(message)

    async def start(self):
        if self._is_running:
            return

        try:
            loop = asyncio.get_running_loop()
            self._server = await loop.create_server(
                lambda: self,
                host=self.address[0],
                port=self.address[1],
                backlog=self.listeners,
                reuse_address=True,
                start_serving=True
            )

            sockets = self._server.sockets
            for sock in sockets:
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self._server_task = asyncio.create_task(self._server.serve_forever())
            self._is_running = True
        except ConnectionRefusedError as err:
            pass

    @property
    def is_running(self):
        return self._is_running
    
    def stop(self):
        self._server.close()

    def update(self):
        for ch in self.channels[:]:
            ch.update()

        for ch in self.channels[:]:
            if ch.transport and ch.transport.is_closing():
                self.channels.remove(ch)