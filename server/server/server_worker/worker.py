import logging
import multiprocessing
import select
import socket
import time
import uuid

from protocol import mrequests, mresponses
from protocol.socket_lib import SizeDataSocket, SizeDataSocketConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(created)s %(process)s %(filename)s [%(lineno)d)]: %(message)s",
)


class Worker(multiprocessing.Process, SizeDataSocket):
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

    def run(self):
        msg_count = 0
        logging.info("Worker started for %s", self.address)
        while self.process_run:
            ready = select.select([self.connection], [], [], 0.1)
            if ready[0]:
                message = mrequests.Base.from_bytes(message=self._recv())
                message_t = type(message)
                msg_count += 1

                if message_t == mrequests.PingRequest:
                    logging.info("Pong!")
                    self._send(self.ping_response_b)
                elif message_t == mrequests.UUIDRequest:
                    logging.info("UUID Request: %s", message)
                    self._send(
                        mresponses.UUIDResponse(
                            title=message.data.title, uuid=uuid.uuid4().hex
                        ).to_bytes()
                    )
                elif message_t == mrequests.CloseRequest:
                    logging.info("Close request")
                    self.send_close()
                elif message_t == mrequests.ShutdownRequest:
                    logging.info("Shutdown request")
                    self.shutdown()
                else:
                    logging.error("Unknown Message: %s", message)

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
