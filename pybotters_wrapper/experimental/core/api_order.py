from typing import Callable, Awaitable, TypeVar, Generic, NamedTuple, Type

from aiohttp.client import ClientResponse

from . import ExchangeAPI
from .._typedefs import TEndpoint, TSymbol, TRequsetMethod
from ..core import APIClient, PriceSizeFormatter

TGenerateEndpointParameters = TypeVar("TGenerateEndpointParameters")
TTranslateParametersParameters = TypeVar("TTranslateParametersParameters")
TWrapResponseParameters = TypeVar("TWrapResponseParameters")
TResponseWrapper = TypeVar("TResponseWrapper")


class OrderAPI(
    Generic[
        TResponseWrapper,
        TGenerateEndpointParameters,
        TTranslateParametersParameters,
        TWrapResponseParameters,
    ],
    ExchangeAPI,
):
    def __init__(
        self,
        api_client: APIClient,
        method: TRequsetMethod,
        *,
        order_id_key: str,
        order_id_extractor: Callable[[ClientResponse, dict, str], str | None]
        | None = None,
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
        price_size_formatter: PriceSizeFormatter | None = None,
        price_format_keys: list[str] | None = None,
        size_format_keys: list[str] | None = None,
    ):
        super(OrderAPI, self).__init__(
            api_client, method, response_decoder=response_decoder
        )
        self._api_client = api_client
        self._method = method
        self._order_id_key = order_id_key
        self._order_id_extractor = order_id_extractor
        self._endpoint_generator = endpoint_generator
        self._parameters_translater = parameters_translater
        self._response_wrapper_cls = response_wrapper_cls
        self._price_size_formatter = price_size_formatter
        self._price_format_keys = price_format_keys or []
        self._size_format_keys = size_format_keys or []

    def _generate_endpoint(self, params: TGenerateEndpointParameters) -> TEndpoint:
        assert self._endpoint_generator is not None
        if isinstance(self._endpoint_generator, str):
            return self._endpoint_generator
        elif callable(self._endpoint_generator):
            return self._endpoint_generator(params)
        else:
            raise TypeError(f"Unsupported: {self._endpoint_generator}")

    def _translate_parameters(self, params: TTranslateParametersParameters) -> dict:
        assert self._parameters_translater is not None
        return self._parameters_translater(params)

    def _wrap_response(self, params: TWrapResponseParameters) -> TResponseWrapper:
        raise self._response_wrapper_cls(params)

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

    def _extract_order_id(
        self,
        resp: ClientResponse,
        resp_data: dict,
    ) -> str | None:
        if self._order_id_extractor is not None:
            return self._order_id_extractor(resp, resp_data, self._order_id_key)
        else:
            return self._default_order_id_extractor(resp, resp_data, self._order_id_key)

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
