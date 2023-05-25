from typing import Literal

from pybotters_wrapper.core.typedefs.typing import TSymbol
from ..core import PriceSizePrecisionFetcher


class bitFlyerPriceSizePrecisionFetcher(PriceSizePrecisionFetcher):
    def fetch_precisions(
        self, cache: bool = True
    ) -> dict[Literal["price", "size"], dict[TSymbol, int]]:
        return {
            "price": {
                "FX_BTC_JPY": 0
            },
            "size": {
                "FX_BTC_JPY": 8
            }
        }