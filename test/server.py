import logging
import os

from pc_server.server.server_head import Head, HeadConfig

from example_protocol.example_worker import Worker

logging.basicConfig(
    level=logging.INFO, format="%(created)s %(process)s %(lineno)s: %(message)s"
)

config = HeadConfig(
    host=os.getenv("SERVER_HOST"),
    port=int(os.getenv("SERVER_PORT")),
    max_workers=int(os.getenv("MAX_WORKERS")),
    socket_timeout_s=float(os.getenv("SOCKET_TIMEOUT_S")),
    Worker=Worker,
)
head = Head(config=config)
