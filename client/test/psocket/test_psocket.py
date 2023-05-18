import logging
import os
import time

import pytest

from protocol import mresponses
from protocol.error import Error

from .client import TestClient, TestClientConfig


@pytest.fixture(scope="session")
def test_client():
    client = TestClient(
        config=TestClientConfig(
            host=os.getenv("SERVER_HOST"),
            port=int(os.getenv("SERVER_PORT")),
            timeout_s=float(os.getenv("SOCKET_TIMEOUT_S")),
        )
    )
    logging.info("Client created.")
    return client


def test_ping(test_client):
    response = test_client.ping()
    assert response == mresponses.PingResponse()


def test_ping_thread(test_client):
    last_comm = test_client.psock.last_recv
    sleep_s = float(os.getenv("SOCKET_TIMEOUT_S"))
    time.sleep(sleep_s)
    assert last_comm != test_client.psock.last_recv


def test_close(test_client):
    response = test_client.close()
    assert response == mresponses.CloseResponse()
    assert test_client.psock.open is False


def test_reconnect(test_client):
    test_client.reconnect()
    test_ping(test_client)


def test_shutdown(test_client):
    response = test_client.send_shutdown()
    assert type(response) == mresponses.ShutdownResponse

    response = test_client.reconnect()
    assert type(response) == Error
