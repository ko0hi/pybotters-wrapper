import pybotters

import pybotters_wrapper as pbw

DUMMY_LISTEN_KEY = "[LISTEN_KEY]"


class BinanceListenKeyFetcher:
    _ENDPOINTS = {
        "binancespot": "/api/v3/userDataStream",
        "binanceusdsm": "/fapi/v1/listenKey",
        "binancecoinm": "/dapi/v1/listenKey",
    }

    def __init__(self, client: pybotters.Client | None = None):
        self._client = client
        self._listenkey = None

    def fetch_listenkey(self, exchange: str) -> str:
        if self._client is None:
            raise RuntimeError("self._client are missing.")
        api = pbw.create_api(exchange, self._client)
        resp = api.spost(self._ENDPOINTS[exchange])
        data = resp.json()
        self._listenkey = data["listenKey"]
        return self._listenkey

    def get_listenkey(self, exchange=None) -> str:
        if self._listenkey is None:
            assert exchange is not None
            return self.fetch_listenkey(exchange)
        return self._listenkey
