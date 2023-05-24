import os

import pytest
from pc_client import BaseClientConfig

from example_protocol.example_client import Client


@pytest.fixture(scope="session")
def test_client() -> Client:
    client = Client(
        config=BaseClientConfig(
            host=os.getenv("SERVER_HOST"),
            port=int(os.getenv("SERVER_PORT")),
            timeout_s=float(os.getenv("SOCKET_TIMEOUT_S")),
        )
    )
    yield client

    if client.psock.is_open():
        client.close()
