from pybotters_wrapper.binance.binanceusdsm import BinanceUSDSMWrapperFactory


def test_exchange_property_biananceusdsm():
    eprop = BinanceUSDSMWrapperFactory.create_exchange_property()
    assert eprop.exchange == "binanceusdsm"
    assert eprop.base_url == "https://fapi.binance.com"
