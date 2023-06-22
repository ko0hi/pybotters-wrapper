from typing import Literal

import requests


from ...core import PriceSizePrecisionFetcher, TSymbol
from ...exceptions import FetchPrecisionsError


class KuCoinFuturesPriceSizePrecisionFetcher(PriceSizePrecisionFetcher):
    def fetch_precisions(self) -> dict[Literal["price", "size"], dict[TSymbol, int]]:
        resp = requests.get("https://api-futures.kucoin.com/api/v1/contracts/active")
        if resp.status_code != 200:
            raise FetchPrecisionsError(f"Failed to fetch precisions: {resp.text}")
        data = resp.json()
        return {
            "price": {
                d["symbol"]: self.value_to_precision(float(d["tickSize"]))
                for d in data["data"]
            },
            "size": {d["symbol"]: int(d["lotSize"]) for d in data["data"]},
        }
