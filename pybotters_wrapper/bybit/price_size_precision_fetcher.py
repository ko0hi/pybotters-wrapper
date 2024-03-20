from typing import Literal

import requests

from ..core import PriceSizePrecisionFetcher, TSymbol
from ..exceptions import FetchPrecisionsError


class BybitPriceSizePrecisionFetcher(PriceSizePrecisionFetcher):
    # TODO: Only "linear" category supported now.
    _CATEGORY: str = "linear"
    def fetch_precisions(self) -> dict[Literal["price", "size"], dict[TSymbol, int]]:
        resp = requests.get(
            "https://api.bybit.com//v5/market/instruments-info", params={"category": self._CATEGORY}
        )
        if resp.status_code != 200:
            raise FetchPrecisionsError(resp.json())
        data = resp.json()

        return {
            "price": {
                d["symbol"]: self.value_to_precision(
                    float(d["priceFilter"]["tickSize"])
                )
                for d in data["result"]["list"]
            },
            "size": {
                d["symbol"]: self.value_to_precision(
                    float(d["lotSizeFilter"]["minOrderQty"])
                )
                for d in data["result"]["list"]
            },
        }
