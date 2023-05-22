from typing import Any, Awaitable, Callable, NamedTuple, Type

from aiohttp.client import ClientResponse

from .api_client import APIClient
from .api_exchange import (
    ExchangeAPI,
    TGenerateEndpointParameters,
    TResponseWrapper,
    TTranslateParametersParameters,
    TWrapResponseParameters,
)
from .normalized_store_orderbook import OrderbookItem
from .._typedefs import TEndpoint, TRequestMethod, TSide


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
            method: TRequestMethod,
            *,
            response_itemizer: Callable[
                                   [ClientResponse, any], dict[
                                       TSide, list[OrderbookItem]]
                               ]
                               | None,
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
        super(FetchAPI, self).__init__(
            api_client,
            method,
            endpoint_generator=endpoint_generator,
            parameter_translater=parameter_translater,
            response_wrapper_cls=response_wrapper_cls,
            response_decoder=response_decoder,
        )

        self._response_itemizer = response_itemizer

    def _itemize_response(
            self, resp: ClientResponse, data: Any | None = None
    ) -> Any:
        assert self._response_itemizer is not None
        return self._response_itemizer(resp, data)
