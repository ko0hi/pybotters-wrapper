from __future__ import annotations

from pybotters_wrapper.common import API
from pybotters_wrapper.utils import BybitUSDTMixin, BybitInverseMixin


class BybitUSDTAPI(BybitUSDTMixin, API):
    BASE_URL = "https://api.bybit.com"


class BybitInverseAPI(BybitInverseMixin, API):
    BASE_URL = "https://api.bybit.com"
