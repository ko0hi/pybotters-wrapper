from typing import Literal

import requests

from ..core import PriceSizePrecisionFetcher, TSymbol
from ..exceptions import FetchPrecisionsError


class bitbankPriceSizePrecisionFetcher(PriceSizePrecisionFetcher):
    def fetch_precisions(self) -> dict[Literal["price", "size"], dict[TSymbol, int]]:
        res = requests.get("https://api.bitbank.cc/v1/spot/pairs")

        data = res.json()
        if data["success"] == 0:
            raise FetchPrecisionsError(
                f"Failed to fetch bitbank precisions {res.json()}"
            )

        return {
            "price": {p["name"]: p["price_digits"] for p in data["data"]["pairs"]},
            "size": {
                p["name"]: self.value_to_precision(float(p["unit_amount"]))
                for p in data["data"]["pairs"]
            },
        }
