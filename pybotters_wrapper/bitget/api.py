from __future__ import annotations

from pybotters_wrapper.common import API
from pybotters_wrapper.utils import BitgetMixin


class BitgetAPI(BitgetMixin, API):
    BASE_URL = "https://api.bitget.com"
