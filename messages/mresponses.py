from .base import Base


class OpenResponse(Base):
    name = "open-res"

    class OpenData:
        status: str

        def __init__(self, status: str = None):
            self.status = status

        def __repr__(self):
            return '{"status": "' + self.status + '"}'

    data: OpenData

    def __init__(self, status: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = OpenResponse.OpenData(status=status)


class PingResponse(Base):
    name = "ping-res"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = None


class CloseResponse(Base):
    name = "close-res"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = None


class UUIDResponse(Base):
    name = "uuid-res"

    class UUIDData:
        title: str
        uuid: str

        def __init__(self, title: str = None, uuid: str = None):
            self.title = title
            self.uuid = uuid

        def __repr__(self):
            ret = {"title": self.title, "uuid": self.uuid}
            return f"{ret}"

    data: UUIDData

    def __init__(self, title: str = None, uuid: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = UUIDResponse.UUIDData(title=title, uuid=uuid)
