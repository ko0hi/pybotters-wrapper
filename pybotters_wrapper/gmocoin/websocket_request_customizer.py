import pybotters

from .token_fetcher import GMOCoinTokenFetcher
from ..core import WebSocketRequestCustomizer


class GMOCoinWebsocketRequestCustomizer(WebSocketRequestCustomizer):
    def __init__(self, client: pybotters.Client = None):
        super(GMOCoinWebsocketRequestCustomizer, self).__init__(client)
        self._token_fetcher = GMOCoinTokenFetcher(client)

    def customize(
        self, endpoint: str, request_list: list[dict | str]
    ) -> tuple[str, list[dict | str]]:
        if "private" in endpoint:
            return f"{endpoint}/{self._token_fetcher.fetch()}", request_list
        else:
            return endpoint, request_list
