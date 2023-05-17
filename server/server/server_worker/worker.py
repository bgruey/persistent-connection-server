import logging
import multiprocessing
import select
import socket
import struct
import time
import typing
import uuid

from messages import mrequests, mresponses

logging.basicConfig(
    level=logging.WARNING, format="%(created)s %(process)s: %(message)s"
)


class Worker(multiprocessing.Process):
    buffer_size: int
    connection: socket.socket
    address: str
    message_parser: typing.Callable[[bytes], typing.Any]
    last_messaged: float
    timeout_s: float
    ping_response_b: bytes
    close_response_b: bytes

    def __init__(self, connection: socket.socket, address: str, timeout_s: float = 5.0):
        self.buffer_size = 65536
        self.connection = connection
        self.address = address
        self.last_messaged = time.time()
        self.timeout_s = timeout_s
        self.ping_response_b = mresponses.PingResponse().to_bytes()
        self.close_response_b = mresponses.CloseResponse().to_bytes()
        super().__init__()
        self.start()

    def run(self):
        msg_count = 0
        logging.error("Worker started with: %s, %s", self.address, self.connection)
        while True:
            ready = select.select([self.connection], [], [], 0.1)
            if ready[0]:
                message = mrequests.Base.from_bytes(message=self.read_data())
                message_t = type(message)
                self.last_messaged = time.time()
                msg_count += 1
                if message_t == mrequests.PingRequest:
                    logging.error("Pong!")
                    self.send_message(self.ping_response_b)
                elif message_t == mrequests.UUIDRequest:
                    logging.error("UUID Request: %s", message)
                    self.send_message(
                        mresponses.UUIDResponse(
                            title=message.data.title, uuid=uuid.uuid4().hex
                        ).to_bytes()
                    )
                elif message_t == mrequests.CloseRequest:
                    self.send_close()
                    break
                else:
                    logging.error("Unknown Message: %s", message)
            elif time.time() - self.last_messaged > self.timeout_s:
                logging.error("Closing due to timeout.")
                self.send_close()
                break

    def send_close(self):
        logging.error("Sending close.")
        self.send_message(self.close_response_b)
        self.connection.close()

    def read_data(self) -> bytes:
        message_size = int(struct.unpack(">I", self.connection.recv(4))[0])
        chunks = []
        bytes_read = 0
        while bytes_read < message_size:
            chunk = self.connection.recv(
                min(message_size - bytes_read, self.buffer_size)
            )
            if chunk == b"":
                raise ConnectionError("Expected bytes in socket, got none.")
            chunks.append(chunk)
            bytes_read += len(chunk)
        logging.error("Worker Read: %s", b"".join(chunks))
        return b"".join(chunks)

    def send_message(self, message: bytes):
        message_size = len(message)
        packet = struct.pack(f">I{message_size}s", message_size, message)
        packet_size = message_size + 4
        sent_size = 0
        while packet:
            n = self.connection.send(packet)
            packet = packet[n:]
            sent_size += n
        if sent_size != packet_size:
            raise ConnectionError(f"Sent only {sent_size} of {packet_size} bytes!")
