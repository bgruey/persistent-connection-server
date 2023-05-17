import logging
import os

from server.server_head.head import Head, HeadConfig

logging.basicConfig(
    level=logging.WARNING, format="%(created)s %(process)s: %(message)s"
)
logging.error("Starting Server Head")

config = HeadConfig(
    host=os.getenv("SERVER_HOST"),
    port=int(os.getenv("SERVER_PORT")),
    max_workers=int(os.getenv("MAX_WORKERS")),
    socket_timeout_s=float(os.getenv("SOCKET_TIMEOUT_S")),
)
head = Head(config=config)

logging.error("Server Finished.")
