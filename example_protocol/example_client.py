from client.client import BaseClient
from .presponses import UUIDResponse
from .prequests import UUIDRequest


class Client(BaseClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_uuid(self, title: str) -> UUIDResponse:
        return UUIDResponse.from_bytes(
            message=self.psock.get_response(
                UUIDRequest(title=title).to_bytes()
            )
        )

