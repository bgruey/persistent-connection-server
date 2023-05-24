from pc_protocol.base import Base


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
