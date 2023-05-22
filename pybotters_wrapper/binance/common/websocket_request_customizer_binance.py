import time

import pybotters

from .listenkey_fetcher import BinanceListenKeyFetcher, DUMMY_LISTEN_KEY
from ...core import WebSocketRequestCustomizer


class BinanceWebSocketRequestCustomizer(WebSocketRequestCustomizer):
    def __init__(self, exchange: str, client: pybotters.Client = None):
        super(BinanceWebSocketRequestCustomizer, self).__init__(client)
        self._exchange = exchange
        self._listenkey_fetcher = BinanceListenKeyFetcher(client)

    def customize(self, endpoint: str, request_list: list[dict]) -> tuple[str, dict]:
        old_params = []
        new_params = []
        for rl in request_list:
            for p in rl["params"]:
                if p not in old_params:
                    old_params.append(p)

        for p in old_params:
            if p == DUMMY_LISTEN_KEY:
                new_params.append(self._listenkey_fetcher.get_listenkey(self._exchange))
            else:
                new_params.append(p)

        new_request_list = {
            "method": "SUBSCRIBE",
            "params": new_params,
            "id": int(time.monotonic() * 10 ** 9),
        }

        return endpoint, new_request_list

    @property
    def listenkey(self):
        return self.listenkey

    def set_client(self, client: pybotters.Client):
        super().set_client(client)
        self._listenkey_fetcher = BinanceListenKeyFetcher(client)
