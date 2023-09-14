from typing import Literal

import requests

from ..core import PriceSizePrecisionFetcher, TSymbol
from ..exceptions import FetchPrecisionsError


class BybitPriceSizePrecisionFetcher(PriceSizePrecisionFetcher):
    def fetch_precisions(self) -> dict[Literal["price", "size"], dict[TSymbol, int]]:
        resp = requests.get(
            "https://api.bybit.com/derivatives/v3/public/instruments-info"
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
                    float(d["lotSizeFilter"]["minTradingQty"])
                )
                for d in data["result"]["list"]
            },
        }
