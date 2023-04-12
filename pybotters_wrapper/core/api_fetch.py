from typing import Awaitable, Callable, Generic, NamedTuple, Type

from aiohttp.client import ClientResponse

from .._typedefs import TEndpoint, TRequsetMethod
from . import APIClient, ExchangeAPI
from .api_exchange import TGenerateEndpointParameters, TResponseWrapper, \
    TTranslateParametersParameters, TWrapResponseParameters


class FetchAPI(
    ExchangeAPI[
        TResponseWrapper,
        TGenerateEndpointParameters,
        TTranslateParametersParameters,
        TWrapResponseParameters,
    ],
):
    """取引所Fetch API実装用のベースクラス。"""

    def __init__(
        self,
        api_client: APIClient,
        method: TRequsetMethod,
        *,
        endpoint_generator: TEndpoint
        | Callable[[TGenerateEndpointParameters], str]
        | None = None,
        parameter_translater: Callable[[TTranslateParametersParameters], dict]
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
            parameters_translater=parameter_translater,
            response_wrapper_cls=response_wrapper_cls,
            response_decoder=response_decoder,
        )
