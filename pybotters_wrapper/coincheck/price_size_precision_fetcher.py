from typing import Literal

from ..core import PriceSizePrecisionFetcher, TSymbol


class CoincheckPriceSizePrecisionFetcher(PriceSizePrecisionFetcher):
    def fetch_precisions(self) -> dict[Literal["price", "size"], dict[TSymbol, int]]:
        return {
            "price": {
                "btc_jpy": 0,
                "etc_jpy": 1,
                "lsk_jpy": 2,
                "mona_jpy": 2,
                "omg_jpy": 2,
                "plt_jpy": 3,
                "fnct_jpy": 3,
                "dai_jpy": 2,
            },
            "size": {
                "btc_jpy": 3,
                "etc_jpy": 0,
                "lsk_jpy": 0,
                "mona_jpy": 0,
                "omg_jpy": 0,
                "plt_jpy": 0,
                "fnct_jpy": 0,
                "dai_jpy": 0,
            },
        }
