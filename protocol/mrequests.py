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
