import os

import pytest

from messages import mrequests, mresponses

from .client import TestClient, TestClientConfig


@pytest.fixture
def test_client():
    client = TestClient(
        config=TestClientConfig(
            host=os.getenv("SERVER_HOST"),
            port=int(os.getenv("SERVER_PORT")),
            timeout_s=float(os.getenv("SOCKET_TIMEOUT_S")),
        )
    )
    client.ping()

    return client


def test_ping(test_client):
    response = test_client.ping()
    assert response == mresponses.PingResponse()


def test_close(test_client):
    response = test_client.close()
    assert response == mresponses.CloseResponse()
