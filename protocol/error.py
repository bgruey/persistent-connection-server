from .base import Base


class Error(Base):
    name = "error"

    class ErrorData:
        code: int
        description: str

        def __init__(self, code: int, description: str):
            self.code = code
            self.description = description

    data: ErrorData

    def __init__(self, code: int = None, description: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = self.ErrorData(code=code, description=description)
