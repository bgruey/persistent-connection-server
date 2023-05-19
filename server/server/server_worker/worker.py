import logging
import multiprocessing
import select
import socket
import time

from protocol import mrequests, mresponses
from protocol.error import ErrorResponse
from protocol.socket_lib import SizeDataSocket

logging.basicConfig(
    level=logging.INFO,
    format="%(created)s %(process)s %(filename)s [%(lineno)d)]: %(message)s",
)


class BaseWorker(multiprocessing.Process, SizeDataSocket):
    connection: socket.socket
    address: str
    server_run: multiprocessing.Value
    process_run: bool
    timeout_s: float

    ping_response_b: bytes
    close_response_b: bytes
    shutdown_response_b: bytes

    def __init__(
        self,
        connection: socket.socket,
        address: str,
        server_run: multiprocessing.Value,
        timeout_s: float = 5.0,
    ):
        SizeDataSocket.__init__(self, sock=connection, timeout_s=timeout_s)
        self.connection = connection
        self.address = address
        self.server_run = server_run
        self.process_run = True
        self.timeout_s = timeout_s

        self.ping_response_b = mresponses.PingResponse().to_bytes()
        self.close_response_b = mresponses.CloseResponse().to_bytes()
        self.shutdown_response_b = mresponses.ShutdownResponse().to_bytes()

        multiprocessing.Process.__init__(self)
        self.start()

    def process(self, message_t, message) -> bool:
        """
        Overload this function to process custom messages. It should have the following:
            - message_t: expected to be the request type
            - message: expected to be message data
            - RETURN: boolean, true if processed and
                      false if message_t was not processed by custom messages.
        """
        return False

    def _process(self, message: bytes):
        message = mrequests.Base.from_bytes(message=message)
        message_t = type(message)
        if self.process(message_t, message):
            return

        if message_t == mrequests.PingRequest:
            self._send(self.ping_response_b)
        elif message_t == mrequests.CloseRequest:
            logging.info("Close request")
            self.send_close()
        elif message_t == mrequests.ShutdownRequest:
            logging.info("Shutdown request")
            self.shutdown()
        else:
            logging.error("Unknown Message: %s", message)

    def _send_error(self, code: int, description: str):
        self._send(message=ErrorResponse(code=code, description=description).to_bytes())

    def run(self):
        logging.info("Worker started for %s", self.address)
        while self.process_run:
            ready = select.select([self.connection], [], [], 0.1)
            if ready[0]:
                try:
                    self._process(message=self._recv())
                except Exception as exc:
                    # Not expected to be used in production where exceptions are
                    # a security issue.
                    self._send_error(code=500, description=str(exc))
            elif time.time() - self.last_recv > self.timeout_s:
                logging.info("Closing due to timeout.")
                self.send_close()

        logging.info("Worker finished for %s", self.address)

    def shutdown(self):
        with self.server_run.get_lock():
            self.server_run.value = 0
        self._send(self.shutdown_response_b)
        self._close()

    def send_close(self):
        self._send(self.close_response_b)
        self._close()

    def _close(self) -> None:
        self.connection.close()
        self.process_run = False
