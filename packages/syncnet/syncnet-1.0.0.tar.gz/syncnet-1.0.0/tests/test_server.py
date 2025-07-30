from unittest import IsolatedAsyncioTestCase
from src.syncnet.server import SyncNetServer
from src.syncnet.channel import SyncNetChannel
from utils.logger import Logger
import asyncio

class TestServer(IsolatedAsyncioTestCase):

    def setUp(self):
        self.server = SyncNetServer(SyncNetChannel)
    
    def test_server_instance(self):
        self.assertIsNotNone(self.server)

    def test_server_run(self):
        asyncio.run(self.server.start())
        Logger.i(f"Server started at address {self.server.address}")

    def tearDown(self):
        if self.server.is_running:
            Logger.i(f"Server stopped at address {self.server.address}")
            self.server.stop()

        