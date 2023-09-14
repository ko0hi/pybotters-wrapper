import pytest

import pybotters_wrapper as pbw


@pytest.mark.skip(reason="access to the real api")
def test_fetch():
    fetcher = pbw.create_factory("kucoinspot").create_price_size_precisions_fetcher()
    precisions = fetcher.fetch_precisions()
    print(precisions)
