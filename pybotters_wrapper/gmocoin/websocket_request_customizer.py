import pybotters

from ..core import WebSocketRequestCustomizer
from .token_fetcher import GMOCoinTokenFetcher


class GMOCoinWebsocketRequestCustomizer(WebSocketRequestCustomizer):
    def __init__(self, client: pybotters.Client = None):
        super(GMOCoinWebsocketRequestCustomizer, self).__init__(client)
        self._token_fetcher: GMOCoinTokenFetcher | None = None

    def customize(
        self, endpoint: str, request_list: list[dict | str]
    ) -> tuple[str, list[dict | str]]:
        if self._token_fetcher is None:
            self._init_token_fetcher()

        assert self._token_fetcher is not None

        if "private" in endpoint:
            return f"{endpoint}/{self._token_fetcher.fetch()}", request_list
        else:
            return endpoint, request_list

    def _init_token_fetcher(self) -> None:
        if self._client is None:
            raise RuntimeError("Client is not set")
        self._token_fetcher = GMOCoinTokenFetcher(self._client)
