from typing import Callable, Awaitable, NamedTuple, TypedDict

from aiohttp.client import ClientResponse

from .api_client import APIClient
from .api_order import OrderAPI
from .._typedefs import TEndpoint, TOrderId, TSymbol, TRequsetMethod


class CancelOrderAPIResponse(NamedTuple):
    order_id: str
    resp: ClientResponse | None = None
    resp_data: dict | None = None


class CancelOrderAPIGenerateEndpointParameters(TypedDict):
    symbol: TSymbol
    order_id: str
    extra_params: dict


class CancelOrderAPITranslateParametersParameters(TypedDict):
    endpoint: TEndpoint
    symbol: TSymbol
    order_id: str
    extra_params: dict


class CancelOrderAPIWrapResponseParameters(TypedDict):
    order_id: str
    resp: ClientResponse
    resp_data: dict


class CancelOrderAPI(
    OrderAPI[
        CancelOrderAPIResponse,
        CancelOrderAPIGenerateEndpointParameters,
        CancelOrderAPITranslateParametersParameters,
        CancelOrderAPIWrapResponseParameters,
    ]
):
    def __init__(
        self,
        api_client: APIClient,
        method: TRequsetMethod,
        order_id_key: str,
        endpoint: TEndpoint | Callable[[TSymbol, TOrderId, dict], str] | None = None,
        parameter_translater: Callable[[TEndpoint, TSymbol, TOrderId, dict], dict]
        | None = None,
        order_id_extractor: Callable[[ClientResponse, dict, str], str | None]
        | None = None,
        response_decoder: Callable[
            [ClientResponse], dict | list | Awaitable[dict | list]
        ]
        | None = None,
    ):
        super(CancelOrderAPI, self).__init__(
            api_client,
            method,
            order_id_key=order_id_key,
            order_id_extractor=order_id_extractor,
            response_decoder=response_decoder,
        )
        self._endpoint = endpoint
        self._parameter_translater = parameter_translater

    async def cancel_order(
        self,
        symbol: TSymbol,
        order_id: TOrderId,
        *,
        extra_params: dict = None,
        request_params: dict = None,
    ) -> CancelOrderAPIResponse:
        extra_params = extra_params or {}
        request_params = request_params or {}
        endpoint = self._generate_endpoint(
            CancelOrderAPIGenerateEndpointParameters(
                symbol=symbol, order_id=order_id, extra_params=extra_params
            )
        )
        parameters = self._translate_parameters(
            CancelOrderAPITranslateParametersParameters(
                endpoint=endpoint,
                symbol=symbol,
                order_id=order_id,
                extra_params=extra_params,
            )
        )
        parameters = {**parameters, **extra_params}
        resp = await self.request(endpoint, parameters, **request_params)
        resp_data = await self._decode_response(resp)
        order_id = self._extract_order_id(resp, resp_data)
        return self._wrap_response(
            CancelOrderAPIWrapResponseParameters(
                order_id=order_id, resp=resp, resp_data=resp_data
            )
        )
