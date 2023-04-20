from pybotters_wrapper.binance.binancecoinm import BinanceCOINMWrapperFactory


def test_exchange_property_biananceusdsm():
    eprop = BinanceCOINMWrapperFactory.create_exchange_property()
    assert eprop.exchange == "binancecoinm"
    assert eprop.base_url == "https://dapi.binance.com"
