import logging
import os
import threading
import time

from client.client import BaseClient, BaseClientConfig
from protocol import mrequests, mresponses

logging.basicConfig(
    level=logging.INFO,
    format="%(created)s %(thread)d %(filename)s %(lineno)s: %(message)s",
)


class Client(BaseClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_uuid(self, title: str) -> mresponses.UUIDResponse:
        r = mrequests.UUIDRequest(title=title)
        logging.error("R: %s", r)
        return mresponses.UUIDResponse.from_bytes(
            message=self.psock.get_response(r.to_bytes())
        )


def thread_pings():
    client = Client(
        config=BaseClientConfig(
            host=os.getenv("SERVER_HOST"),
            port=int(os.getenv("SERVER_PORT")),
            timeout_s=float(os.getenv("SOCKET_TIMEOUT_S")),
        )
    )
    for i in range(1):
        client.ping()
        time.sleep(2)

    time.sleep(10)
    logging.info(client.get_uuid(title="title data value"))
    client.close()
    logging.error("Closed")


threads = []
for i in range(1):
    threads.append(threading.Thread(target=thread_pings))
    threads[-1].start()
for thread in threads:
    thread.join()
