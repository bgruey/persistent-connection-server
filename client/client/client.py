import types

from messages import mresponses

from .psocket import PersistentSocket, PSocketConfig


class BaseClientConfig:
    psocket_config: PSocketConfig

    def __init__(
        self,
        host: str,
        port: int,
        timeout_s: float,
        buffer_size: int = 65536,
    ):
        self.psocket_config = PSocketConfig(
            host=host, port=port, timeout_s=timeout_s, buffer_size=buffer_size
        )


class BaseClient:
    config: BaseClientConfig
    psock: PersistentSocket

    def __init__(self, config: BaseClientConfig):
        self.config = config
        self.psock = PersistentSocket(config=config.psocket_config)

    def close(self) -> mresponses.CloseResponse:
        return self.psock.close()

    def ping(self) -> mresponses.PingResponse:
        return self.psock.ping()
