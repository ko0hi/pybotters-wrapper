import pytest

from pybotters_wrapper.core.exchange_property import ExchangeProperty


def test_exchange_property():
    eprop = ExchangeProperty(
        {"base_url": "sample_base_url", "exchange": "sample_exchange"}
    )
    assert eprop.base_url == "sample_base_url"
    assert eprop.exchange == "sample_exchange"


def test_exchange_property_with_invalid_config():
    with pytest.raises(ValueError) as e:
        # typehint error should occur
        ExchangeProperty({"base_url": "sample_base_url"})
    assert str(e.value) == "Missing properties: ['exchange']"
