import logging
import socket
import json
import struct
import time
import uuid


class ClientConfig:
    host: str
    port: int
    timeout_s: float
    buffer_size: int

    def __init__(self, host: str, port: int, timeout_s: float, buffer_size: int = 65536):
        self.host = host
        self.port = port
        self.timeout_s = timeout_s
        self.buffer_size = buffer_size

    def get_connect_tuple(self):
        return self.host, self.port


class Client:
    config: ClientConfig
    sock: socket.socket
    send_message: dict
    recv_message: dict

    def __init__(self, config: ClientConfig):
        self.config = config
        self._clear_send_message()
        self._clear_recv_message()
        self._connect()

    def _clear_recv_message(self):
        self.recv_message = {
            "name": "",
            "data": None
        }

    def _clear_send_message(self):
        self.send_message = {
            "name": "",
            "data": None
        }

    def _connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.config.get_connect_tuple())

    def _send(self):
        message_bytes = json.dumps(self.send_message)
        message_size = len(message_bytes)
        packet = struct.pack(
            f">I{message_size}s",
            message_size, message_bytes.encode("UTF-8")
        )
        packet_size = message_size + 4
        sent_size = 0
        while packet:
            n = self.sock.send(packet)
            packet = packet[n:]
            sent_size += n
        if sent_size != packet_size:
            raise ConnectionError(f"Sent only {sent_size} of {packet_size} bytes!")

    def _recv(self):
        message_size = int(
            struct.unpack(">I", self.sock.recv(4))[0]
        )
        chunks = []
        bytes_read = 0
        while bytes_read < message_size:
            chunk = self.sock.recv(min(message_size - bytes_read, self.config.buffer_size))
            if chunk == b"":
                raise ConnectionError("Expected bytes in socket, got none.")
            chunks.append(chunk)
            bytes_read += len(chunk)
        self.recv_message = json.loads(b"".join(chunks))

    def ping(self):
        logging.error("Ping!")
        self._clear_send_message()
        self.send_message["name"] = "ping-req"
        self._send()
        self._recv()
        if self.recv_message["name"] != "ping-res":
            raise Exception(
                f"Not 'ping-res': {self.recv_message['name']} <--> {self.recv_message['name'] == 'ping-res'}"
            )

    def close(self):
        self._clear_send_message()
        self.send_message["name"] = "close"
        self._send()
        self._recv()
        if self.recv_message["name"] != "close":
            raise Exception(f"Wrong Response in close: {self.recv_message}")
        self.sock.close()
