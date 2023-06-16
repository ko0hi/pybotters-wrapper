import pytest

from pybotters_wrapper.gmocoin.price_size_precision_fetcher import \
    GMOCoinPriceSizePrecisionFetcher


@pytest.mark.skip(reason="Access to the real API")
def test_fetch_precisions():
    precisions = GMOCoinPriceSizePrecisionFetcher().fetch_precisions()
    print(precisions)