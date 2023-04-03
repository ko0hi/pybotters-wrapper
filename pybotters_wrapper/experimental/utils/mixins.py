import math

import requests
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

    def format_precision(
        self, symbol: str, value: float, price_or_size: str
    ) -> str:
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


class _BinanceExchangeMixin(ExchangeMixin):
    _EXCHANGE_INFO_ENDPOINT = None

    def get_precisions_from_exchange_info(self, data):
        price_precisions = {}
        size_precisions = {}

        for s in data["symbols"]:
            symbol = s["symbol"]
            tick_size = eval(
                [f for f in s['filters'] if
                 f['filterType'] == 'PRICE_FILTER'][0]['tickSize']
            )
            price_precision = int(math.log10(float(tick_size)) * -1)
            step_size = eval(
                [f for f in s['filters'] if f['filterType'] == 'LOT_SIZE'][0]['stepSize']
            )
            size_precision = int(math.log10(step_size) * -1)
            price_precisions[symbol] = price_precision
            size_precisions[symbol] = size_precision
        return price_precisions, size_precisions

    def fetch_exchange_info(self) -> requests.Response:
        assert self._EXCHANGE_INFO_ENDPOINT is not None
        resp = requests.get(self._EXCHANGE_INFO_ENDPOINT)
        if resp.status_code != 200:
            msg = f"Failed to fetch binance exchange info: {self._EXCHANGE_INFO_ENDPOINT}"
            logger.error(msg)
            raise RuntimeError(msg)
        return resp

    def fetch_precisions(self) -> tuple[dict, dict]:
        assert self._EXCHANGE_INFO_ENDPOINT is not None
        resp = self.fetch_exchange_info()
        return self.get_precisions_from_exchange_info(resp.json())

    def load_precisions(self):
        try:
            (
                self._PRICE_PRECISIONS[self.exchange],
                self._SIZE_PRECISIONS[self.exchange],
            ) = self.fetch_precisions()
        except RuntimeError:
            super().load_precisions()


class BinanceSpotMixin(_BinanceExchangeMixin):
    _EXCHANGE_NAME = "binancespot"
    _EXCHANGE_INFO_ENDPOINT = "https://api.binance.com/api/v3/exchangeInfo"


class BinanceUSDSMMixin(_BinanceExchangeMixin):
    _EXCHANGE_NAME = "binanceusdsm"
    _EXCHANGE_INFO_ENDPOINT = "https://fapi.binance.com/fapi/v1/exchangeInfo"


class BinanceUSDSMTESTMixin(_BinanceExchangeMixin):
    _EXCHANGE_NAME = "binanceusdsm_test"
    _EXCHANGE_INFO_ENDPOINT = "https://testnet.binancefuture.com/fapi/v1/exchangeInfo"


class BinanceCOINMMixin(_BinanceExchangeMixin):
    _EXCHANGE_NAME = "binancecoinm"
    _EXCHANGE_INFO_ENDPOINT = "https://dapi.binance.com/dapi/v1/exchangeInfo"

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


class BinanceCOINMTESTMixin(_BinanceExchangeMixin):
    _EXCHANGE_NAME = "binancecoinm_test"
    _EXCHANGE_INFO_ENDPOINT = "https://testnet.binancefuture.com/dapi/v1/exchangeInfo"


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
