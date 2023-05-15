import logging
import os
import random
import time
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
        time.sleep(random.randint(0, 3))
    sleep_t = random.randint(1, 20)
    #time.sleep(sleep_t)
    try:
        client.close()
        logging.error("Closed after %s seconds", sleep_t)
    except Exception as exc:
        logging.error("ERROR closed after %s seconds: %s", sleep_t, exc)


threads = []
for i in range(20):
    threads.append(
        threading.Thread(target=thread_pings)
    )
    threads[-1].start()
for thread in threads:
    thread.join()

