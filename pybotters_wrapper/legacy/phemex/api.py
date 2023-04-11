from __future__ import annotations

from legacy.core import API
from pybotters_wrapper.utils.mixins import PhemexMixin


class PhemexAPI(PhemexMixin, API):
    BASE_URL = "https://api.phemex.com"
