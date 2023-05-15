import logging
import os
import threading

from client.client import ClientConfig, Client
logging.basicConfig(
    level=logging.WARNING,
    format='%(created)s %(thread)d %(filename)s: %(message)s'
)


def thread_pings():
    client = Client(
        config=ClientConfig(
            host=os.getenv("SERVER_HOST"),
            port=int(os.getenv("SERVER_PORT")),
            timeout_s=float(os.getenv("SOCKET_TIMEOUT_S"))
        )
    )

    for _ in range(10):
        client.ping()
    client.close()
    logging.error("Closed")


threads = []
for i in range(20):
    threads.append(
        threading.Thread(target=thread_pings)
    )
    threads[-1].start()
for thread in threads:
    thread.join()

