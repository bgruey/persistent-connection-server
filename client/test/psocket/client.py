from client.client import BaseClient, BaseClientConfig
from messages import mrequests, mresponses


class TestClientConfig(BaseClientConfig):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TestClient(BaseClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_uuid(self, title: str) -> mresponses.UUIDResponse:
        return mresponses.UUIDResponse(
            message=self.psock.get_response(
                mrequests.UUIDRequest(title=title).to_bytes()
            )
        )
