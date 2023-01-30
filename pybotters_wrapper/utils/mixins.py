from loguru import logger

from .io import read_resource


class LoggingMixin:
    def log(self, msg, level="debug", verbose=True):
        if verbose:
            getattr(logger, level)(f"[{self.__class__.__name__}] {msg}")


class ExchangeMixin:
    _EXCHANGE_NAME = None
    _PRICE_PRECISIONS: dict[str, dict[str, int]] = {}
    _SIZE_PRECISIONS: dict[str, dict[str, int]] = {}

    def load_precisions(self):
        self._PRICE_PRECISIONS = {}
        self._SIZE_PRECISIONS = {}
        try:
            self._PRICE_PRECISIONS[self.exchange] = read_resource(
                self._price_precision_filename()
            )
            self._SIZE_PRECISIONS[self.exchange] = read_resource(
                self._size_precision_filename()
            )
        except FileNotFoundError:
            self._PRICE_PRECISIONS[self.exchange] = {}
            self._SIZE_PRECISIONS[self.exchange] = {}

    def format_precision(self, symbol: str, value: float, price_or_size: str) -> str:
        precisions = self._get_precision_resource(price_or_size)
        precision = self._lookup_precision(symbol, precisions)
        return self._format_by_precision(value, precision)

    def format_price(self, symbol: str, price: float) -> str:
        return self.format_precision(symbol, price, "price")

    def format_size(self, symbol: str, size: float) -> str:
        return self.format_precision(symbol, size, "size")

    def _price_precision_filename(self) -> str:
        return f"{self.exchange}_price_precision.json"

    def _size_precision_filename(self) -> str:
        return f"{self.exchange}_size_precision.json"

    def _get_precision_resource(self, price_or_size: str) -> dict:
        if self.exchange not in self._PRICE_PRECISIONS:
            self.load_precisions()

        if price_or_size == "price":
            return self._PRICE_PRECISIONS[self.exchange]
        elif price_or_size == "size":
            return self._SIZE_PRECISIONS[self.exchange]
        else:
            raise RuntimeError(f"Unsupported: {price_or_size}")

    def _lookup_precision(self, symbol: str, precisions: dict) -> int | None:
        if symbol in precisions:
            return precisions[symbol]
        else:
            return None

    def _format_by_precision(self, value: float, precision: int | None) -> str:
        if precision is not None:
            if precision == 0:
                return str(int(value))
            else:
                return str(round(value, precision))
        else:
            return str(value)

    @property
    def exchange(self) -> str:
        if self._EXCHANGE_NAME is None:
            raise RuntimeError("_EXCHANGE_NAME has not been set")
        return self._EXCHANGE_NAME

    @property
    def package(self) -> str:
        # pybotters_wrapper.${package}
        return self.__module__.split(".")[1]


class BinanceSpotMixin(ExchangeMixin):
    _EXCHANGE_NAME = "binancespot"


class BinanceUSDSMMixin(ExchangeMixin):
    _EXCHANGE_NAME = "binanceusdsm"


class BinanceUSDSMTESTMixin(ExchangeMixin):
    _EXCHANGE_NAME = "binanceusdsm_test"


class BinanceCOINMMixin(ExchangeMixin):
    _EXCHANGE_NAME = "binancecoinm"

    def _lookup_precision(self, symbol: str, precisions: dict) -> int | None:
        if symbol in precisions:
            return precisions[symbol]
        else:
            # perpのものを参照する
            symbol_perp = symbol.split("_")[0] + "_PERP"
            if symbol_perp in precisions:
                return precisions[symbol_perp]
            else:
                return None


class BinanceCOINMTESTMixin(ExchangeMixin):
    _EXCHANGE_NAME = "binancecoinm_test"


class bitbankMixin(ExchangeMixin):
    _EXCHANGE_NAME = "bitbank"


class bitflyerMixin(ExchangeMixin):
    _EXCHANGE_NAME = "bitflyer"


class BitgetMixin(ExchangeMixin):
    _EXCHANGE_NAME = "bitget"


class BybitUSDTMixin(ExchangeMixin):
    _EXCHANGE_NAME = "bybitusdt"


class BybitInverseMixin(ExchangeMixin):
    _EXCHANGE_NAME = "bybitinverse"


class CoincheckMixin(ExchangeMixin):
    _EXCHANGE_NAME = "coincheck"


class GMOCoinMixin(ExchangeMixin):
    _EXCHANGE_NAME = "gmocoin"


class KuCoinSpotMixin(ExchangeMixin):
    _EXCHANGE_NAME = "kucoinspot"


class KuCoinFuturesMixin(ExchangeMixin):
    _EXCHANGE_NAME = "kucoinfutures"


class OKXMixin(ExchangeMixin):
    _EXCHANGE_NAME = "okx"


class PhemexMixin(ExchangeMixin):
    _EXCHANGE_NAME = "phemex"
