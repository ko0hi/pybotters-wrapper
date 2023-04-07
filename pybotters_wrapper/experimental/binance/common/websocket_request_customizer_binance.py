import time

import pybotters

from ...core import WebSocketRequestCustomizer
from .listenkey_fetcher import BinanceListenKeyFetcher, DUMMY_LISTEN_KEY


class BinanceWebSocketRequestCustomizer(WebSocketRequestCustomizer):
    def __init__(self, exchange: str, client: pybotters.Client = None):
        super(BinanceWebSocketRequestCustomizer, self).__init__(client)
        self._exchange = exchange
        self._listenkey_fetcher = BinanceListenKeyFetcher(client)

    def customize(self, endpoint: str, request_list: dict) -> tuple[str, dict]:
        new_params = []
        for p in request_list["params"]:
            if p == DUMMY_LISTEN_KEY:
                new_params.append(self._listenkey_fetcher.get_listenkey(self._exchange))
            else:
                new_params.append(p)

        new_request_list = {
            "method": "SUBSCRIBE",
            "params": new_params,
            "id": int(time.monotonic() * 10**9),
        }

        return endpoint, new_request_list

    @property
    def listenkey(self):
        return self.listenkey
