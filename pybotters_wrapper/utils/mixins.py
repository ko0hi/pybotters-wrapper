class ExchangeMixin:
    _NAME = None

    @property
    def exchange(self) -> str:
        if self._NAME is None:
            raise RuntimeError("_EXCHANGE_NAME has not been set")
        return self._NAME


class BinanceSpotMixin(ExchangeMixin):
    _NAME = "binancespot"


class BinanceUSDSMMixin(ExchangeMixin):
    _NAME = "binanceusdsm"


class BinanceCOINMMixin(ExchangeMixin):
    _NAME = "binancecoinm"


class bitbankMixin(ExchangeMixin):
    _NAME = "bitbank"


class bitflyerMixin(ExchangeMixin):
    _NAME = "bitflyer"


class BitgetMixin(ExchangeMixin):
    _NAME = "bitget"


class BybitUSDTMixin(ExchangeMixin):
    _NAME = "bybitusdt"


class BybitInverseMixin(ExchangeMixin):
    _NAME = "bybitinverse"


class CoincheckMixin(ExchangeMixin):
    _NAME = "coincheck"


class GMOCoinMixin(ExchangeMixin):
    _NAME = "gmocoin"


class KuCoinSpotMixin(ExchangeMixin):
    _NAME = "kucoinspot"


class KuCoinFuturesMixin(ExchangeMixin):
    _NAME = "kucoinfutures"


class OKXMixin(ExchangeMixin):
    _NAME = "okx"


class PhemexMixin(ExchangeMixin):
    _NAME = "phemex"
