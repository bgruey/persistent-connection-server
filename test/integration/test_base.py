import pytest
import time
import os
from pc_protocol import mresponses

from .fixture_example_client import test_client, Client


def test_ping(test_client: Client):
    response = test_client.ping()
    assert response == mresponses.PingResponse()


def test_ping_thread(test_client: Client):
    last_comm = test_client.psock.last_recv
    start = time.time()
    timeout_s = float(os.getenv("SOCKET_TIMEOUT_S"))
    while last_comm == test_client.psock.last_recv:
        time.sleep(0.1)
        if time.time() - start > timeout_s:
            raise TimeoutError("No recv update in timeout seconds.")
    assert True


def test_reconnect(test_client: Client):
    response = test_client.close()
    assert response == mresponses.CloseResponse()
    assert test_client.psock.open is False
    test_client.reconnect()
    test_ping(test_client)
    test_ping_thread(test_client)


@pytest.mark.order(-1)
def test_shutdown(test_client: Client):
    response = test_client.send_shutdown()
    assert response == mresponses.ShutdownResponse()
    try:
        test_client.reconnect()
        raise Exception("Successfully reconnected after sending shutdown request.")
    except Exception as exc:
        logging.info("Failed Reconnect as expected: %s", exc)
