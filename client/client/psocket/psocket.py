import logging
import threading
import time
import typing

from protocol import mrequests, mresponses
from protocol.socket_lib import SizeDataSocket, SizeDataSocketConfig


def thread_lock_wrapper(func):
    def wrapper(*args, **kwargs):
        with args[0].lock:
            args[0].last_communication = time.time()
            return func(*args, **kwargs)

    return wrapper


class PSocketConfig(SizeDataSocketConfig):
    pass


class PersistentSocket(SizeDataSocket):
    config: PSocketConfig
    lock: threading.Lock
    ping_thread: threading.Thread
    ping_run: bool

    close_request_b: bytes
    ping_request_b: bytes

    def __init__(self, config: PSocketConfig):
        self.config = config
        self.lock = threading.Lock()

        self.open_request_b = mrequests.OpenRequest().to_bytes()
        self.close_request_b = mrequests.CloseRequest().to_bytes()
        self.ping_request_b = mrequests.PingRequest().to_bytes()

        super().__init__(
            config=config,
        )
        self.start_ping_thread()

    def _ping_thread_func(self):
        ping_s = self.config.timeout_s * 0.75
        if not ping_s > 0:
            logging.info("No sleep_s, ping thread exiting.")
            return
        while self.ping_run:
            try:
                if time.time() - self.last_recv > ping_s:
                    self.send_ping()
                time.sleep(0.25)
            except Exception as exc:
                logging.error("Ping failed, exiting ping thread: %s", exc)
                break

    def start_ping_thread(self):
        self.ping_run = True
        self.ping_thread = threading.Thread(target=self._ping_thread_func)
        self.ping_thread.start()

    def stop_ping(self):
        self.ping_run = False
        self.ping_thread.join()

    @thread_lock_wrapper
    def get_response(self, message: bytes) -> bytes:
        return self._send_and_recv(message)

    @thread_lock_wrapper
    def send_ping(self) -> mresponses.PingResponse:
        response = mresponses.PingResponse(
            message=self._send_and_recv(self.ping_request_b)
        )
        if response.name != mresponses.PingResponse.name:
            raise Exception(f"Wrong response in ping: {response}")
        return response

    def close(self, send: bool = True) -> typing.Optional[mresponses.CloseResponse]:
        if self.ping_run:
            self.stop_ping()
        if send:
            response = mresponses.CloseResponse(
                message=self._send_and_recv(self.close_request_b)
            )
            if response.name != mresponses.CloseResponse.name:
                raise Exception(f"Wrong response in close: {response}")
        self._close()
        if send:
            return response  # noqa
