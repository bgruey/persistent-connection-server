import logging
import socket
import struct
import threading
import time

from messages import mrequests, mresponses


def thread_lock_wrapper(func):
    def wrapper(*args, **kwargs):
        with args[0].lock:
            return func(*args, **kwargs)

    return wrapper


class PSocketConfig:
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


class PersistentSocket:
    config: PSocketConfig
    sock: socket.socket
    lock: threading.Lock
    ping_thread: threading.Thread
    open: bool
    ping_request_b: bytes
    close_request_b: bytes

    def __init__(self, config: PSocketConfig):
        self.config = config
        self.lock = threading.Lock()
        self._connect()
        self.ping_request_b = mrequests.PingRequest().to_bytes()
        self.close_request_b = mrequests.CloseRequest().to_bytes()
        self._run_ping_thread()

    def _run_ping_thread(self):
        def ping_thread(psock: "PersistentSocket"):
            sleep_s = psock.config.timeout_s * 0.5
            logging.error("Sleeping %s seconds per ping in thread.", sleep_s)
            if not sleep_s > 0:
                logging.error("No sleep_s, ping thread exiting.")
                return
            while psock.open:
                try:
                    psock.ping()
                    time.sleep(sleep_s)
                except Exception as exc:
                    logging.error("Ping failed, exiting ping thread: %s", exc)
                    break

        self.ping_thread = threading.Thread(target=ping_thread, args=(self,))
        self.ping_thread.start()

    @thread_lock_wrapper
    def get_response(self, message: bytes) -> bytes:
        return self._send_and_recv(message)

    def _send_and_recv(self, message: bytes) -> bytes:
        self._send(message)
        return self._recv()

    def _connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.config.get_connect_tuple())
        self.open = True

    def _send(self, message: bytes):
        logging.error("P Socket Send: %s", message)
        message_size = len(message)
        packet = struct.pack(f">I{message_size}s", message_size, message)
        packet_size = message_size + 4
        sent_size = 0
        while packet:
            n = self.sock.send(packet)
            packet = packet[n:]
            sent_size += n
        if sent_size != packet_size:
            raise ConnectionError(f"Sent only {sent_size} of {packet_size} bytes!")

    def _recv(self) -> bytes:
        message_size = int(struct.unpack(">I", self.sock.recv(4))[0])
        chunks = []
        bytes_read = 0
        while bytes_read < message_size:
            chunk = self.sock.recv(
                min(message_size - bytes_read, self.config.buffer_size)
            )
            if chunk == b"":
                raise ConnectionError("Expected bytes in socket, got none.")
            chunks.append(chunk)
            bytes_read += len(chunk)
        return b"".join(chunks)

    @thread_lock_wrapper
    def ping(self) -> mresponses.PingResponse:
        logging.error("Ping!")
        response = mresponses.PingResponse(
            message=self._send_and_recv(self.ping_request_b)
        )
        if response.name != mresponses.PingResponse.name:
            raise Exception(f"Wrong response in ping: {response}")
        return response

    @thread_lock_wrapper
    def close(self) -> mresponses.CloseResponse:
        logging.error("Close.")
        response = mresponses.CloseResponse(
            message=self._send_and_recv(self.close_request_b)
        )
        self.sock.close()
        self.open = False
        if response.name != mresponses.CloseResponse.name:
            raise Exception(f"Wrong response in close: {response}")
        return response
