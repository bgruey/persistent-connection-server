import os

import pytest
from pc_client import BaseClientConfig

from example_protocol.example_client import Client
from pc_protocol.error import ErrorResponse
from pc_protocol.mresponses import ShutdownResponse


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

    response = client.send_shutdown()
    assert type(response) == ShutdownResponse

    try:
        response = client.reconnect()
        assert type(response) == ErrorResponse
        assert response.data.code == 400
        assert response.data.description == "Shutting down, not accepting connections."
    except (ConnectionRefusedError, ConnectionResetError):
        pass
    except Exception as exc:
        raise Exception(str(exc))
