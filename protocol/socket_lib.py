import socket
import struct
import time
import typing

from .error import ErrorResponse
from .mrequests import OpenRequest
from .mresponses import Base, OpenResponse

MESSAGE_SIZE_SZ = 4


def send_message(sock: socket.socket, message: bytes):
    message_size = len(message)
    packet = struct.pack(f">I{message_size}s", message_size, message)
    packet_size = message_size + MESSAGE_SIZE_SZ
    sent_size = 0
    while packet:
        n = sock.send(packet)
        packet = packet[n:]
        sent_size += n
    if sent_size != packet_size:
        raise ConnectionError(f"Sent {sent_size} of {packet_size} bytes!")


def recv_message(sock: socket.socket, buffer_size: int = 65536) -> bytes:
    message_size = int(struct.unpack(">I", sock.recv(4))[0])
    chunks = []
    bytes_read = 0
    while bytes_read < message_size:
        chunk = sock.recv(min(message_size - bytes_read, buffer_size))
        if chunk == b"":
            raise ConnectionError("Expected bytes in socket, got none.")
        chunks.append(chunk)
        bytes_read += len(chunk)
    return b"".join(chunks)


class SizeDataSocketConfig:
    host: str
    port: int
    timeout_s: float
    buffer_size: int

    def __init__(
        self, host: str, port: int, timeout_s: float, buffer_size: int = 65536
    ):
        self.host = host
        self.port = port
        self.timeout_s = timeout_s
        self.buffer_size = buffer_size

    def get_connect_tuple(self):
        return self.host, self.port


class SizeDataSocket:
    """
    Socket client that utilizes the size-data protocol:
        - send the size of the data as an integer
        - send the data as bytes
    """

    config: SizeDataSocketConfig
    sock: socket.socket
    open: bool
    open_request_b: bytes
    last_recv: float
    last_times: typing.Dict[str, float]

    def __init__(
        self,
        sock: socket.socket = None,
        config: SizeDataSocketConfig = None,
        timeout_s: float = None,
    ):
        self.open_request_b = OpenRequest().to_bytes()
        self.open = False
        self.last_recv = 0.0
        self.last_times = {
            "s_send": 0.0,
            "e_send": 0.0,
            "s_recv": 0.0,
            "e_recv": 0.0
        }

        if sock:
            if timeout_s is None:
                timeout_s = 0
            self.sock = sock
            self.open = True
            self.config = SizeDataSocketConfig(
                host=self.sock.getsockname()[0],
                port=self.sock.getsockname()[1],
                timeout_s=timeout_s,
            )
            self.sock.settimeout(self.config.timeout_s)
        elif config:
            self.config = config
            self.open = False
            self.connect()
        else:
            raise ValueError("Empty SizeDataSocket Constructor is invalid.")

    def calc_last_times(self) -> typing.Tuple[float, float]:
        last_send = self.last_times["e_send"] - self.last_times["s_send"]
        last_recv = self.last_times["e_recv"] - self.last_times["s_recv"]
        return last_send, last_recv

    def connect(self) -> typing.Union[OpenResponse, ErrorResponse]:
        if self.open:
            raise Exception("Connecting to open socket.")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(self.config.timeout_s)
        self.sock.connect(self.config.get_connect_tuple())
        self.open = True
        open_response = Base.from_bytes(
            message=self._send_and_recv(self.open_request_b)
        )
        if type(open_response) == ErrorResponse:
            self.open = False
            return open_response
        elif type(open_response) != OpenResponse:
            raise ConnectionError("Did not receive OpenResponse: %s", open_response)
        return open_response

    def _close(self):
        self.open = False
        self.sock.close()

    def _send_and_recv(self, message: bytes) -> bytes:
        self._send(message)
        return self._recv()

    def _send(self, message: bytes):
        self.last_times["s_send"] = time.perf_counter()
        send_message(self.sock, message)
        self.last_times["e_send"] = time.perf_counter()

    def _recv(self) -> bytes:
        self.last_recv = time.time()
        self.last_times["s_recv"] = time.perf_counter()
        message = recv_message(self.sock, self.config.buffer_size)
        self.last_times["e_recv"] = time.perf_counter()
        return message
