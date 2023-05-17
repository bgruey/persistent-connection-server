import typing

import jsonpickle


class Base:
    name: str
    data: typing.Any

    def __init__(self, *args, **kwargs):
        if kwargs.get("message"):
            self.from_bytes(kwargs.get("message"))

    def to_bytes(self):
        return jsonpickle.dumps(self).encode("UTF-8")

    @staticmethod
    def from_bytes(message: bytes):
        return jsonpickle.loads(message.decode("UTF-8"))

    def __repr__(self):
        ret = {"name": self.name, "data": repr(self.data)}
        return f"{ret}"
