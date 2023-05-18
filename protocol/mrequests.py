from .base import Base


class OpenRequest(Base):
    name = "open-req"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = None


class PingRequest(Base):
    name = "ping-req"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = None


class CloseRequest(Base):
    name = "close-req"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = None


class ShutdownRequest(Base):
    name = "shutdown-req"
    data: None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = None


class UUIDRequest(Base):
    name = "uuid-req"

    class UUIDData:
        title: str

        def __init__(self, title: str = None):
            self.title = title

        def __repr__(self):
            ret = {"title": self.title}
            return f"{ret}"

    data: UUIDData

    def __init__(self, title: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = UUIDRequest.UUIDData(title=title)
