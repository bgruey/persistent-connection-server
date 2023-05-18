import logging
import multiprocessing
import socket
import uuid

from protocol import mrequests, mresponses
from server.server_worker.worker import BaseWorker


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
        """
        Overload this function to process custom messages. It should have the following:
            - message_t: expected to be the request type
            - message: expected to be message data
            - RETURN: boolean, true if processed and
                      false if message_t was not processed by custom messages.
        """
        if message_t == mrequests.UUIDRequest:
            logging.info("UUID Request: %s", message)
            self._send(
                mresponses.UUIDResponse(
                    title=message.data.title, uuid=uuid.uuid4().hex
                ).to_bytes()
            )
            return True
        return False
