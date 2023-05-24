import math
import time
import typing

from .fixture_example_client import test_client, Client


def avg_std(data: typing.List[float], factor: float = 1.0e3, decimals: int = 3):
    avg = sum(data) / len(data)
    std = math.sqrt(sum(pow(e - avg, 2) for e in data) / (len(data) - 1.0))
    return round(avg * factor, decimals), round(std * factor, decimals)


def test_no_40ms_delay(test_client: Client):
    """
    Nagle's Algorithm coupled with Delayed Ack can introduce a 40ms
    delay in send/acls.
    """
    n = 100
    sends = [0.0] * n
    recvs = [0.0] * n
    for i in range(n):
        test_client.ping()
        send, recv = test_client.psock.calc_last_times()
        sends[i] = send
        recvs[i] = recv
    time.sleep(10)
    unit = 1.0e3  # ms
    avg_sends = avg_std(sends[1:], unit)
    avg_recvs = avg_std(recvs[1:], unit)
    assert avg_sends[0] < 40.0
    assert avg_recvs[0] < 40.0
