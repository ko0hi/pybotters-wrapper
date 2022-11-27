from __future__ import annotations

from pybotters_wrapper.common import API
from pybotters_wrapper.utils.mixins import OKXMixin


class OKXAPI(API):
    BASE_URL = "https://www.okx.com"
