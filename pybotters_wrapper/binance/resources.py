from __future__ import annotations

from pybotters_wrapper.utils import read_resource

SPOT_PRICE_PRECISIONS = read_resource("binancespot_price_precision.json")
SPOT_SIZE_PRECISIONS = read_resource("binancespot_size_precision.json")
USDSM_PRICE_PRECISIONS = read_resource("binanceusdsm_price_precision.json")
USDSM_SIZE_PRECISIONS = read_resource("binanceusdsm_size_precision.json")
COINM_PRICE_PRECISIONS = read_resource("binancecoinm_price_precision.json")
COINM_SIZE_PRECISIONS = read_resource("binancecoinm_size_precision.json")
