import logging
import os

from example_worker import Worker

from server.server_head.head import Head, HeadConfig

logging.basicConfig(
    level=logging.INFO, format="%(created)s %(process)s %(lineno)s: %(message)s"
)
logging.info("Starting Server Head")

config = HeadConfig(
    host=os.getenv("SERVER_HOST"),
    port=int(os.getenv("SERVER_PORT")),
    max_workers=int(os.getenv("MAX_WORKERS")),
    socket_timeout_s=float(os.getenv("SOCKET_TIMEOUT_S")),
    Worker=Worker,
)
head = Head(config=config)

logging.info("Server Finished.")
