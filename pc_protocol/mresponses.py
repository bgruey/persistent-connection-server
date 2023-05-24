from .base import Base


class OpenResponse(Base):
    name = "open-res"

    class OpenData:
        status: str
        process_id: int

        def __init__(self, status: str, pid: int):
            self.status = status
            self.process_id = pid

        def __repr__(self):
            return '{"status": "' + repr(self.status) + '"}'

    data: OpenData

    def __init__(self, status: str, pid: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = OpenResponse.OpenData(status=status, pid=pid)

    def update_pid(self, pid: int):
        self.data.process_id = pid


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
