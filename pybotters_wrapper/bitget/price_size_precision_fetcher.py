from typing import Literal

import requests

from ..core import PriceSizePrecisionFetcher, TSymbol


class BitgetPriceSizePrecisionFetcher(PriceSizePrecisionFetcher):
    def fetch_precisions(self) -> dict[Literal["price", "size"], dict[TSymbol, int]]:
        data = self._fetch_info()
        return {
            "price": {d["symbol"].split("_")[0]: int(d["pricePlace"]) for d in data},
            "size": {d["symbol"].split("_")[0]: int(d["volumePlace"]) for d in data},
        }

    @classmethod
    def _fetch_info(cls) -> list[dict]:
        url = "https://api.bitget.com/api/mix/v1/market/contracts?productType=umcbl"
        resp = requests.get(url)
        if resp.status_code == 200:
            return resp.json()["data"]
        else:
            raise RuntimeError(f"Failed to fetch price size precision:{resp.text}")
