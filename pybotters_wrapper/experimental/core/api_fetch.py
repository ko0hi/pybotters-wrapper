from typing import Callable, Awaitable, Type, NamedTuple

from aiohttp.client import ClientResponse

from . import APIClient, ExchangeAPI
from .api_exchange import TGenerateEndpointParameters, TTranslateParametersParameters
from .._typedefs import TEndpoint, TRequsetMethod


class FetchAPI(ExchangeAPI):
    """取引所Fetch API実装用のベースクラス。"""

    def __init__(
        self,
        api_client: APIClient,
        method: TRequsetMethod,
        *,
        endpoint_generator: TEndpoint
        | Callable[[TGenerateEndpointParameters], str]
        | None = None,
        parameters_translater: Callable[[TTranslateParametersParameters], dict]
        | None = None,
        response_wrapper_cls: Type[NamedTuple] = None,
        response_decoder: Callable[
            [ClientResponse], dict | list | Awaitable[dict | list]
        ]
        | None = None,
    ):
        super(ExchangeAPI, self).__init__(
            api_client,
            method,
            endpoint_generator=endpoint_generator,
            parameters_translater=parameters_translater,
            response_wrapper_cls=response_wrapper_cls,
            response_decoder=response_decoder,
        )
