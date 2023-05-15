import logging
import socket
import time
import typing
from ..server_worker.worker import Worker


class HeadConfig:
    host: str
    port: int
    max_workers: int
    socket_timeout_s: float
    inactive_stop_s: int

    def __init__(
            self,
            host: str,
            port: int,
            max_workers: int,
            socket_timeout_s: float,
            inactive_stop_s: int = 0):
        self.host = host
        self.port = port
        self.max_workers = max_workers
        self.socket_timeout_s = socket_timeout_s
        self.inactive_stop_s = inactive_stop_s


class Head:
    config: HeadConfig
    listening_socket: socket.socket
    workers: typing.List[Worker]

    def __init__(self, config: HeadConfig):
        self.config = config
        self.workers = []
        self._connect()
        self._run()

    def _connect(self):
        self.listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listening_socket.settimeout(0.2)
        self.listening_socket.bind((self.config.host, self.config.port))
        self.listening_socket.listen(100)

    def _clean_workers(self) -> int:
        finished_workers = []
        for i, worker in enumerate(self.workers):
            if not worker.is_alive():
                finished_workers.append(i)
        for i in finished_workers:
            del self.workers[i]
        return len(self.workers)

    def add_worker(self, conn: socket.socket, addr: str) -> typing.Optional[Worker]:
        self._clean_workers()
        if len(self.workers) < self.config.max_workers:
            self.workers.append(Worker(
                connection=conn,
                address=addr,
                timeout_s=self.config.socket_timeout_s
            ))
            return self.workers[-1]

    def _run(self):
        logging.error("Starting Server")
        last_added_connection = time.time()
        while True:
            try:
                conn, addr = self.listening_socket.accept()
                logging.error("Starting process for: %s, %s", addr, conn)
                add_attempt = time.time()
                while True:
                    if self.add_worker(conn, addr):
                        last_added_connection = time.time()
                        break
                    time.sleep(0.1)
                    if time.time() - add_attempt > self.config.socket_timeout_s:
                        conn.close()
                        break

            except socket.timeout:
                pass

            if 0 < self.config.inactive_stop_s < time.time() - last_added_connection:
                break
