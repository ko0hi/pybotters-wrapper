from typing import Awaitable, Callable, NamedTuple, Type

from aiohttp.client import ClientResponse

from .._typedefs import TEndpoint, TRequestMethod, TSymbol
from .api_client import APIClient
from .api_exchange import ExchangeAPI, TGenerateEndpointParameters, TResponseWrapper, \
    TTranslateParametersParameters, TWrapResponseParameters
from .formatter_precision import PriceSizeFormatter


class OrderAPI(
    ExchangeAPI[
        TResponseWrapper,
        TGenerateEndpointParameters,
        TTranslateParametersParameters,
        TWrapResponseParameters,
    ]
):
    def __init__(
        self,
        api_client: APIClient,
        method: TRequestMethod,
        *,
        order_id_key: str,
        order_id_extractor: Callable[[ClientResponse, dict, str], str | None]
        | None = None,
        price_size_formatter: PriceSizeFormatter | None = None,
        price_format_keys: list[str] | None = None,
        size_format_keys: list[str] | None = None,
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
        super(OrderAPI, self).__init__(
            api_client,
            method,
            endpoint_generator=endpoint_generator,
            parameter_translater=parameter_translater,
            response_wrapper_cls=response_wrapper_cls,
            response_decoder=response_decoder,
        )
        self._order_id_key = order_id_key
        self._order_id_extractor = order_id_extractor
        self._price_size_formatter = price_size_formatter
        self._price_format_keys = price_format_keys or []
        self._size_format_keys = size_format_keys or []

    def _extract_order_id(
        self,
        resp: ClientResponse,
        resp_data: dict,
    ) -> str | None:
        if self._order_id_extractor is not None:
            return self._order_id_extractor(resp, resp_data, self._order_id_key)
        else:
            return self._default_order_id_extractor(resp, resp_data, self._order_id_key)

    def _format_price(self, parameters: dict, symbol: TSymbol) -> dict:
        if self._price_size_formatter:
            for k in self._price_format_keys:
                parameters[k] = self._price_size_formatter.format(
                    symbol, parameters[k], "price"
                )
        return parameters

    def _format_size(self, parameters: dict, symbol: TSymbol) -> dict:
        if self._price_size_formatter:
            for k in self._size_format_keys:
                parameters[k] = self._price_size_formatter.format(
                    symbol, parameters[k], "size"
                )
        return parameters

    @classmethod
    def _default_order_id_extractor(
        cls, resp: ClientResponse, resp_data: dict, order_id_key: str
    ) -> str | None:
        if resp.status == 200:
            order_id = resp_data
            for k in order_id_key.split("."):
                order_id = order_id[k]
            return str(order_id)
        else:
            return None
