from loguru import logger


class LoggingMixin:
    def log(self, msg, level="debug", verbose=True):
        if verbose:
            getattr(logger, level)(f"[{self.__class__.__name__}] {msg}")


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


class BinanceUSDSMTESTMixin(ExchangeMixin):
    _NAME = "binanceusdsm_test"


class BinanceCOINMMixin(ExchangeMixin):
    _NAME = "binancecoinm"


class BinanceCOINMTESTMixin(ExchangeMixin):
    _NAME = "binancecoinm_test"


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
