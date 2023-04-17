from pybotters_wrapper.binance.binancecoinm import create_binancecoinm_exchange_property


def test_exchange_property_biananceusdsm():
    eprop = create_binancecoinm_exchange_property()
    assert eprop.exchange == "binancecoinm"
    assert eprop.base_url == "https://dapi.binance.com"
