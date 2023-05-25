from typing import Literal

from ..core import PriceSizePrecisionFetcher, TSymbol


class bitFlyerPriceSizePrecisionFetcher(PriceSizePrecisionFetcher):
    def fetch_precisions(self) -> dict[Literal["price", "size"], dict[TSymbol, int]]:
        return {"price": {"FX_BTC_JPY": 0}, "size": {"FX_BTC_JPY": 8}}
