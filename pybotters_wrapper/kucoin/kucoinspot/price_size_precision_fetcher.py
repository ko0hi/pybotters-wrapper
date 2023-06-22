from typing import Literal

import requests


from ...core import PriceSizePrecisionFetcher, TSymbol
from ...exceptions import FetchPrecisionsError


class KuCoinSpotPriceSizePrecisionFetcher(PriceSizePrecisionFetcher):
    def fetch_precisions(self) -> dict[Literal["price", "size"], dict[TSymbol, int]]:
        resp = requests.get("https://api.kucoin.com/api/v2/symbols")
        if resp.status_code != 200:
            raise FetchPrecisionsError(f"Failed to fetch precisions: {resp.text}")
        data = resp.json()

        return {
            "price": {
                d["symbol"]: self.value_to_precision(float(d["priceIncrement"]))
                for d in data["data"]
            },
            "size": {
                d["symbol"]: self.value_to_precision(float(d["baseMinSize"]))
                for d in data["data"]
            },
        }
