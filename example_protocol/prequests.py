from pc_protocol.base import Base


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
