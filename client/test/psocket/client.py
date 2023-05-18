from client.client import BaseClient, BaseClientConfig
from protocol import mrequests, mresponses


class TestClientConfig(BaseClientConfig):
    __test__ = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TestClient(BaseClient):
    __test__ = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_uuid(self, title: str) -> mresponses.UUIDResponse:
        return mresponses.UUIDResponse(
            message=self.psock.get_response(
                mrequests.UUIDRequest(title=title).to_bytes()
            )
        )
