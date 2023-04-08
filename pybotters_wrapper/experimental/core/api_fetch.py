from typing import Callable, Awaitable

from aiohttp.client import ClientResponse

from . import APIClient, ExchangeAPI
from .._typedefs import TRequsetMethod


class FetchAPI(ExchangeAPI):
    """ 取引所Fetch API実装用のベースクラス。
    """
    def __init__(
        self,
        api_client: APIClient,
        method: TRequsetMethod,
        *,
        response_decoder: Callable[
            [ClientResponse], dict | list | Awaitable[dict | list]
        ]
        | None = None,
    ):
        super(ExchangeAPI, self).__init__(
            api_client, method, response_decoder=response_decoder
        )
