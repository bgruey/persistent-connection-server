import logging
import multiprocessing
import socket
import uuid

from pc_server.server_worker.worker import BaseWorker

from .prequests import UUIDRequest
from .presponses import UUIDResponse


class Worker(BaseWorker):
    def __init__(
        self,
        connection: socket.socket,
        address: str,
        server_run: multiprocessing.Value,
        timeout_s: float = 5.0,
    ):
        BaseWorker.__init__(self, connection, address, server_run, timeout_s)

    def process(self, message_t, message) -> bool:
        if message_t == UUIDRequest:
            self._send(
                UUIDResponse(title=message.data.title, uuid=uuid.uuid4().hex).to_bytes()
            )
            return True
        return False
