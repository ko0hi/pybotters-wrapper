import math

import requests
from loguru import logger
from pybotters_wrapper.core.fetcher_price_size_precisions import (
    PriceSizePrecisionFetcher,
)


class BinancePriceSizePrecisionsFetcher(PriceSizePrecisionFetcher):
    _ENDPOINTS = {
        "binancespot": "https://api.binance.com/api/v3/exchangeInfo",
        "binanceusdsm": "https://fapi.binance.com/fapi/v1/exchangeInfo",
        "binanceusdsm_test": "https://testnet.binancefuture.com/fapi/v1/exchangeInfo",
        "bianancecoinm": "https://dapi.binance.com/dapi/v1/exchangeInfo",
        "bianancecoinm_test": "https://testnet.binancefuture.com/dapi/v1/exchangeInfo",
    }

    def __init__(self, exchange: str):
        self._exchange = exchange
        self._precisions = None
        self._exchange_info = None

    def fetch_precisions(self, cache: bool = True) -> dict:
        if self._precisions is not None and cache:
            return self._precisions
        self._exchange_info = self.fetch_exchange_info()
        self._precisions = self._extract_precisions_from_exchange_info(
            self._exchange_info
        )
        return self._precisions

    def fetch_exchange_info(self) -> dict:
        resp = requests.get(self._ENDPOINTS[self._exchange])
        if resp.status_code != 200:
            msg = f"Failed to fetch binance exchange info {resp.json()}"
            logger.error(msg)
            raise RuntimeError(msg)
        return resp.json()

    @classmethod
    def _extract_precisions_from_exchange_info(cls, data: dict) -> dict:
        price_precisions = {}
        size_precisions = {}

        for s in data["symbols"]:
            symbol = s["symbol"]
            tick_size = eval(
                [f for f in s["filters"] if f["filterType"] == "PRICE_FILTER"][0][
                    "tickSize"
                ]
            )
            price_precision = int(math.log10(float(tick_size)) * -1)
            step_size = eval(
                [f for f in s["filters"] if f["filterType"] == "LOT_SIZE"][0][
                    "stepSize"
                ]
            )
            size_precision = int(math.log10(step_size) * -1)
            price_precisions[symbol] = price_precision
            size_precisions[symbol] = size_precision
        return {"price": price_precisions, "size": size_precisions}
