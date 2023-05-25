from typing import NamedTuple, TypedDict

from aiohttp.client import ClientResponse

from .order_api import OrderAPI
from .order_api_builder import OrderAPIBuilder
from ...typedefs import TEndpoint, TSymbol, TSide, TSize, TPrice


class StopMarketOrderAPIResponse(NamedTuple):
    order_id: str
    resp: ClientResponse | None = None
    data: dict | None = None


class StopMarketOrderAPIGenerateEndpointParameters(TypedDict):
    symbol: TSymbol
    side: TSide
    size: TSize
    trigger: TPrice
    extra_params: dict


class StopMarketOrderAPITranslateParametersParameters(TypedDict):
    endpoint: TEndpoint
    symbol: TSymbol
    side: TSide
    size: TSize
    trigger: TPrice
    extra_params: dict


class StopMarketOrderAPIWrapResponseParameters(TypedDict):
    order_id: str
    resp: ClientResponse
    data: dict


class StopMarketOrderAPI(
    OrderAPI[
        StopMarketOrderAPIResponse,
        StopMarketOrderAPIGenerateEndpointParameters,
        StopMarketOrderAPITranslateParametersParameters,
        StopMarketOrderAPIWrapResponseParameters,
    ]
):
    async def stop_market_order(
        self,
        symbol: TSymbol,
        side: TSide,
        size: TSize,
        trigger: TPrice,
        *,
        extra_params: dict = None,
        request_params: dict = None,
    ) -> StopMarketOrderAPIResponse:
        extra_params = extra_params or {}
        request_params = request_params or {}
        endpoint = self._generate_endpoint(
            StopMarketOrderAPIGenerateEndpointParameters(
                symbol=symbol,
                side=side,
                size=size,
                trigger=trigger,
                extra_params=extra_params,
            )
        )
        parameters = self._translate_parameters(
            StopMarketOrderAPITranslateParametersParameters(
                endpoint=endpoint,
                symbol=symbol,
                side=side,
                size=size,
                trigger=trigger,
                extra_params=extra_params,
            )
        )
        parameters = {**parameters, **extra_params}
        parameters = self._format_size(parameters, symbol)
        resp = await self.request(endpoint, parameters, **request_params)
        data = await self._decode_response(resp)
        order_id = self._extract_order_id(resp, data)
        return self._wrap_response(
            StopMarketOrderAPIWrapResponseParameters(
                order_id=order_id, resp=resp, data=data
            )
        )


class StopMarketOrderAPIBuilder(
    OrderAPIBuilder[
        StopMarketOrderAPI,
        StopMarketOrderAPIGenerateEndpointParameters,
        StopMarketOrderAPITranslateParametersParameters,
        StopMarketOrderAPIWrapResponseParameters,
    ]
):
    def __init__(self):
        super(StopMarketOrderAPIBuilder, self).__init__(
            StopMarketOrderAPI, StopMarketOrderAPIResponse
        )
