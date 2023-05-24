from pc_client.client import BaseClient

from .prequests import UUIDRequest
from .presponses import UUIDResponse


class Client(BaseClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_uuid(self, title: str) -> UUIDResponse:
        return UUIDResponse.from_bytes(
            message=self.psock.get_response(UUIDRequest(title=title).to_bytes())
        )
