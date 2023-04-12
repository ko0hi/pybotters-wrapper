from pybotters_wrapper.binance.binanceusdsm.factory_binanceusdsm import \
    create_binanceusdsm_exchange_property


def test_exchange_property_biananceusdsm():
    eprop = create_binanceusdsm_exchange_property()
    assert eprop.exchange == "binanceusdsm"
    assert eprop.base_url == "https://fapi.binance.com"
