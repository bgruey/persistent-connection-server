import logging
import os
import threading
import time
import typing
import math

from client.client import BaseClientConfig
from example_protocol.example_client import Client

logging.basicConfig(
    level=logging.INFO,
    format="%(created)s %(thread)d %(filename)s %(lineno)s: %(message)s",
)


def avg_std(data: typing.List[float], factor: float = 1.0e3, decimals: int = 3):
    avg = sum(data) / len(data)
    std = math.sqrt(
        sum(
            pow(e - avg, 2) for e in data
        ) / (len(data) - 1.0)
    )
    return round(avg * factor, decimals), round(std * factor, decimals)


def test_ping_performance(client: Client, n: int):
    sends = [0.0] * n
    recvs = [0.0] * n
    for i in range(n):
        client.ping()
        send, recv = client.psock.calc_last_times()
        sends[i] = send
        recvs[i] = recv
    time.sleep(10)
    unit = 1.0e3  # ms
    # logging.info("Sends: %s", sends)
    # logging.info("Recvs: %s", recvs)
    return [avg_std(sends[1:], unit), avg_std(recvs[1:], unit)]


client = Client(
    config=BaseClientConfig(
        host=os.getenv("SERVER_HOST"),
        port=int(os.getenv("SERVER_PORT")),
        timeout_s=float(os.getenv("SOCKET_TIMEOUT_S")),
    )
)
logging.info("Single Thread Pings: %s", test_ping_performance(client, 100))


def thread_pings():
    client = Client(
        config=BaseClientConfig(
            host=os.getenv("SERVER_HOST"),
            port=int(os.getenv("SERVER_PORT")),
            timeout_s=float(os.getenv("SOCKET_TIMEOUT_S")),
        )
    )
    logging.info("Thread %s Ping Perf: %s", threading.get_ident(), test_ping_performance(client, 100))
    client.close()


threads = []
for i in range(10):
    threads.append(threading.Thread(target=thread_pings))
    threads[-1].start()
time.sleep(1)
client.send_shutdown()
for thread in threads:
    logging.info("Joining thread %s", thread.ident)
    thread.join()

logging.info("Completed")
