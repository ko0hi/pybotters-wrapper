from __future__ import annotations

from pybotters_wrapper.common import API
from pybotters_wrapper.utils.mixins import GMOCoinMixin


class GMOCoinAPI(GMOCoinMixin, API):
    BASE_URL = "https://api.coin.z.com"
