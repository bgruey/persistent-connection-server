from .base import Base


class OpenResponse(Base):
    name = "open-res"

    class OpenData:
        status: str

        def __init__(self, status: str = None):
            self.status = status

        def __repr__(self):
            return '{"status": "' + repr(self.status) + '"}'

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


class ShutdownResponse(Base):
    name = "shutdown-res"
    data: None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = None
