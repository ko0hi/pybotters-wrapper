from typing import Literal
import requests

from ..core import PriceSizePrecisionFetcher, TSymbol


class OKXPriceSizePrecisionFetcher(PriceSizePrecisionFetcher):
    def fetch_precisions(self) -> dict[Literal["price", "size"], dict[TSymbol, int]]:
        inst_types = ["MARGIN"]
        data = []
        for it in inst_types:
            data += self._fetch_info(it)
        return {
            "price": {
                d["instId"]: self.value_to_precision(float(d["tickSz"])) for d in data
            },
            "size": {
                d["instId"]: self.value_to_precision(float(d["lotSz"])) for d in data
            },
        }

    @classmethod
    def _fetch_info(cls, inst_type: str) -> list[dict]:
        url = f"https://www.okx.com/api/v5/public/instruments?instType={inst_type}"
        resp = requests.get(url)
        if resp.status_code == 200:
            return resp.json()["data"]
        else:
            raise RuntimeError(f"Failed to fetch price size precision:{resp.text}")
