from __future__ import annotations

from pybotters_wrapper.core import API
from pybotters_wrapper.utils.mixins import BitgetMixin


class BitgetAPI(BitgetMixin, API):
    BASE_URL = "https://api.bitget.com"
