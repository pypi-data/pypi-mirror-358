# streaming/proxy.py

import asyncio
import zmq
import zmq.asyncio
from ..utils.ports import PortManager
from ..utils.logger import logger
from ..utils.shared_state import SharedState

class XPubXSubProxy:
    def __init__(self):
        self.ctx = zmq.asyncio.Context.instance()
        self.xpub_socket = None
        self.xsub_socket = None
        self.xpub_port = None
        self.xsub_port = None
        self._running = False
        self.proxy_task = None
        self.shared_state = SharedState.get_instance()

    async def start(self):
        self._running = True
        self.xpub_socket = self.ctx.socket(zmq.XPUB)
        self.xsub_socket = self.ctx.socket(zmq.XSUB)
        
        # Get ports from shared state
        self.xpub_port, self.xsub_port = self.shared_state.get("Orcustrator.XPub"), self.shared_state.get("Orcustrator.XSub")

        xpub_addr = f"tcp://*:{self.xpub_port}"
        xsub_addr = f"tcp://*:{self.xsub_port}"

        self.xpub_socket.bind(xpub_addr)
        self.xsub_socket.bind(xsub_addr)

        self.proxy_task = asyncio.create_task(self._run_proxy())

        logger.success(f"Pub: {self.xpub_port} | Sub: {self.xsub_port} started.")
        command_port = self.shared_state.get("Orcustrator.CommandPort")
        if command_port:
            logger.success(f"All publishers can be controller externally at: {command_port}")

    async def _run_proxy(self):
        poller = zmq.asyncio.Poller()
        poller.register(self.xpub_socket, zmq.POLLIN)
        poller.register(self.xsub_socket, zmq.POLLIN)

        while self._running:
            socks = dict(await poller.poll())
            if socks.get(self.xpub_socket) == zmq.POLLIN:
                msg = await self.xpub_socket.recv_multipart()
                await self.xsub_socket.send_multipart(msg)

            if socks.get(self.xsub_socket) == zmq.POLLIN:
                msg = await self.xsub_socket.recv_multipart()
                await self.xpub_socket.send_multipart(msg)

    async def stop(self):
        self._running = False
        if self.proxy_task:
            self.proxy_task.cancel()
            try:
                await self.proxy_task
            except asyncio.CancelledError:
                pass

        if self.xpub_socket:
            self.xpub_socket.close()
        if self.xsub_socket:
            self.xsub_socket.close()

        # Release the ports
        if self.xpub_port:
            PortManager.release_port(self.xpub_port)
        if self.xsub_port:
            PortManager.release_port(self.xsub_port)