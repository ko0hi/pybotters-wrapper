import pybotters

from .core import APIClient
from .binance.binanceusdsm import create_binanceusdsm_apiclient


def create_client(
    apis: dict[str, list[str]] | str | None = None,
    base_url: str = "",
    **kwargs: any,
) -> pybotters.Client:
    return pybotters.Client(apis, base_url, **kwargs)


def create_api(exchange: str, client: pybotters.Client) -> APIClient:
    return create_binanceusdsm_apiclient(client)
