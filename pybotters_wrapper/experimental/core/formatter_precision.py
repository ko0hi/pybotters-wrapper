from typing import Literal
from .formatter import Formatter
from .._typedefs import TSymbol


class PrecisionFormatter(Formatter):
    def __init__(self, precisions: dict[str, int]):
        self._precisions = precisions

    def format(self, key: str, value: float) -> str:
        precision = self._precisions.get(key)
        if precision:
            if precision == 0:
                return str(int(value))
            else:
                return str(round(value, precision))
        else:
            return str(value)


class PriceSizeFormatter(Formatter):
    def __init__(self, price_precisions: dict, size_precisions: dict):
        self._price_formatter = PrecisionFormatter(price_precisions)
        self._size_formatter = PrecisionFormatter(size_precisions)

    def format(
        self, symbol: TSymbol, value: float, price_or_size: Literal["price", "size"]
    ) -> str:
        if price_or_size == "price":
            formatter = self._price_formatter
        elif price_or_size == "size":
            formatter = self._size_formatter
        else:
            raise TypeError(f"Unsupported: {price_or_size}")
        return formatter.format(symbol, value)
