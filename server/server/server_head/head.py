import logging
import multiprocessing
import socket
import time
import typing

from protocol import error, mrequests, mresponses
from protocol.socket_lib import recv_message, send_message

from ..server_worker.worker import BaseWorker


class HeadConfig:
    host: str
    port: int
    max_workers: int
    socket_timeout_s: float
    inactive_stop_s: int
    Worker: typing.Type[BaseWorker]

    def __init__(
        self,
        host: str,
        port: int,
        max_workers: int,
        socket_timeout_s: float,
        Worker: typing.Type[BaseWorker],  # noqa
    ):
        self.host = host
        self.port = port
        self.max_workers = max_workers
        self.socket_timeout_s = socket_timeout_s
        self.Worker = Worker


class Head:
    config: HeadConfig
    listening_socket: socket.socket
    workers: typing.Dict[int, BaseWorker]
    open_message_ok_b: bytes
    run: multiprocessing.Value

    def __init__(self, config: HeadConfig):
        self.config = config
        self.open_message_ok_b = mresponses.OpenResponse(status="OK").to_bytes()
        self.run = multiprocessing.Value("i", 1)
        self.workers = {}
        self._connect()
        self._run()

    def _connect(self):
        self.listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listening_socket.settimeout(1)
        self.listening_socket.bind((self.config.host, self.config.port))
        self.listening_socket.listen(100)

    def _clean_workers(self) -> int:
        finished_workers = []
        for pid, worker in self.workers.items():
            if not worker.is_alive():
                finished_workers.append(pid)
        for pid in finished_workers:
            del self.workers[pid]
        return len(self.workers)

    def add_worker(self, conn: socket.socket, addr: str) -> typing.Optional[BaseWorker]:
        self._clean_workers()
        if len(self.workers) < self.config.max_workers:
            send_message(conn, self.open_message_ok_b)
            worker = self.config.Worker(
                connection=conn,
                address=addr,
                timeout_s=self.config.socket_timeout_s,
                server_run=self.run,
            )

            self.workers[worker.pid] = worker
            return self.workers[worker.pid]

    def _run(self):
        logging.info("Starting Server")
        while self.run.value:
            try:
                conn, addr = self.listening_socket.accept()
                conn.settimeout(self.config.socket_timeout_s)
                request = mrequests.Base.from_bytes(recv_message(conn))
                if type(request) == mrequests.OpenRequest:
                    if self.run.value:
                        self.add_worker(conn, addr)
                    else:
                        send_message(
                            conn,
                            error.ErrorResponse(
                                code=400,
                                description="Shutting down, not accepting connections.",
                            ).to_bytes(),
                        )
                        conn.close()
                else:
                    send_message(
                        conn,
                        error.ErrorResponse(
                            code=400,
                            description=f"Invalid open request: {request.name}",
                        ).to_bytes(),
                    )
                    conn.close()
                    continue

            except socket.timeout:
                logging.info("No active connections, timed out waiting.")
        logging.info("Shutting down")
        self.listening_socket.close()
        while self._clean_workers():
            time.sleep(1)
