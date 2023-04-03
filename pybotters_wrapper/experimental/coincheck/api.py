from __future__ import annotations

from pybotters_wrapper.core import API
from pybotters_wrapper.utils.mixins import CoincheckMixin


class CoincheckAPI(CoincheckMixin, API):
    BASE_URL = "https://coincheck.com"
