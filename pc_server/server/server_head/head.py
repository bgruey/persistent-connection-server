import logging
import multiprocessing
import socket
import time
import typing

from pc_protocol import error, mrequests, mresponses
from pc_protocol.socket_lib import recv_message, send_message

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
    open_message_ok: mresponses.OpenResponse
    run: multiprocessing.Value

    def __init__(self, config: HeadConfig):
        self.config = config
        self.open_message_ok = mresponses.OpenResponse(status="OK", pid=0)
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
        logging.info("%s", [(k, v) for k, v in self.workers.items()])
        for pid, worker in self.workers.items():
            worker.join(0.05)
            if not worker.is_alive():
                finished_workers.append(pid)
        for pid in finished_workers:
            del self.workers[pid]
        return len(self.workers)

    def add_worker(self, conn: socket.socket, addr: str) -> typing.Optional[BaseWorker]:
        self._clean_workers()
        if len(self.workers) < self.config.max_workers:
            worker = self.config.Worker(
                connection=conn,
                address=addr,
                timeout_s=self.config.socket_timeout_s,
                server_run=self.run,
            )

            self.workers[worker.pid] = worker
            self.open_message_ok.update_pid(worker.pid)
            send_message(conn, self.open_message_ok.to_bytes())
            return self.workers[worker.pid]

    def _run(self):
        logging.info("Starting Server")
        shutdown_iterations = 0
        while shutdown_iterations < 10:
            try:
                if not self.run.value:
                    shutdown_iterations += 1
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
                pass
        logging.info("Shutting down server.")
        self.listening_socket.close()
        while self._clean_workers():
            logging.info(
                "Waiting for %s workers to finish: (%s)",
                len(self.workers),
                self.workers,
            )
            time.sleep(0.5)
