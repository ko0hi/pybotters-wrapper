from ...core.exchange_property import ExchangeProperty


class BinanceUSDSMExchangeProperty(ExchangeProperty):
    @property
    def base_url(self) -> str:
        return "https://fapi.binance.com"

    @property
    def exchange(self) -> str:
        return "binanceusdsm"
