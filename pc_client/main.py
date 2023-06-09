import logging
import os
import threading
import time

from client.client import BaseClientConfig

from example_protocol.example_client import Client

logging.basicConfig(
    level=logging.INFO,
    format="%(created)s %(thread)d %(filename)s %(lineno)s: %(message)s",
)


def thread_pings():
    client = Client(
        config=BaseClientConfig(
            host=os.getenv("SERVER_HOST"),
            port=int(os.getenv("SERVER_PORT")),
            timeout_s=float(os.getenv("SOCKET_TIMEOUT_S")),
        )
    )
    for _ in range(10):
        client.ping()

    time.sleep(10)
    client.get_uuid(title="title data value")
    client.close()


threads = []
for i in range(20):
    threads.append(threading.Thread(target=thread_pings))
    threads[-1].start()
for thread in threads:
    thread.join()
