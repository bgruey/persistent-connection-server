import logging

from protocol import mrequests, mresponses

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

    def get_response(self, message: bytes):
        return self.psock.get_response(message)

    def reconnect(self):
        response = self.psock.connect()
        if type(response) != mresponses.OpenResponse:
            raise ConnectionRefusedError(response.data.description)

        self.psock.start_ping_thread()
        return response

    def close(self) -> mresponses.CloseResponse:
        return self.psock.close()

    def ping(self) -> mresponses.PingResponse:
        return self.psock.send_ping()

    def send_shutdown(self) -> mresponses.ShutdownResponse:
        self.psock.stop_ping()
        logging.info("Sending shutdown request.")
        response = mresponses.ShutdownResponse(
            message=self.psock.get_response(mrequests.ShutdownRequest().to_bytes())
        )
        if response.name != mresponses.ShutdownResponse.name:
            raise ConnectionError("Did not receive ShutdownResponse: %s", response)
        self.psock.close(send=False)
        logging.info("Shutdown response: %s", response)
        return response
