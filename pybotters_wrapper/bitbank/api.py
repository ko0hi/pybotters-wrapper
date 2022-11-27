from __future__ import annotations

from pybotters_wrapper.common import API
from pybotters_wrapper.utils import bitbankMixin


class bitbankAPI(bitbankMixin, API):
    BASE_URL = "https://api.bitbank.cc"
