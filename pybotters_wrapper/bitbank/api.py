from __future__ import annotations

from pybotters_wrapper.core import API
from pybotters_wrapper.utils.mixins import bitbankMixin


class bitbankAPI(bitbankMixin, API):
    BASE_URL = "https://api.bitbank.cc"
