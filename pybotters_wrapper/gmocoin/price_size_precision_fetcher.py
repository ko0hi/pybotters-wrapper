from typing import Literal

import requests

from ..core import PriceSizePrecisionFetcher, TSymbol


class GMOCoinPriceSizePrecisionFetcher(PriceSizePrecisionFetcher):
    def fetch_precisions(self) -> dict[Literal["price", "size"], dict[TSymbol, int]]:
        data = self._fetch_info()
        return {
            "price": {
                d["symbol"]: self.value_to_precision(float(d["tickSize"])) for d in data
            },
            "size": {
                d["symbol"]: self.value_to_precision(float(d["minOrderSize"]))
                for d in data
            },
        }

    @classmethod
    def _fetch_info(cls) -> list[dict]:
        url = "https://api.coin.z.com/public/v1/symbols"
        resp = requests.get(url)
        if resp.status_code == 200:
            return resp.json()["data"]
        else:
            raise RuntimeError(f"Failed to fetch price size precision:{resp.json()}")
