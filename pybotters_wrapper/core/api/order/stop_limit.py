from typing import Any, NamedTuple, TypedDict, cast

from aiohttp.client import ClientResponse

from .order_api import OrderAPI
from .order_api_builder import OrderAPIBuilder
from ...typedefs import (
    TEndpoint,
    TSymbol,
    TSide,
    TPrice,
    TSize,
    TTrigger,
)


class StopLimitOrderAPIResponse(NamedTuple):
    order_id: str
    resp: ClientResponse
    data: Any = None


class StopLimitOrderAPIGenerateEndpointParameters(TypedDict):
    symbol: TSymbol
    side: TSide
    price: TPrice
    size: TSize
    trigger: TPrice
    extra_params: dict


class StopLimitOrderAPITranslateParametersParameters(TypedDict):
    endpoint: TEndpoint
    symbol: TSymbol
    side: TSide
    price: TPrice
    size: TSize
    trigger: TPrice
    extra_params: dict


class StopLimitOrderAPIWrapResponseParameters(TypedDict):
    order_id: str | None
    resp: ClientResponse
    data: Any


class StopLimitOrderAPI(
    OrderAPI[
        StopLimitOrderAPIResponse,
        StopLimitOrderAPIGenerateEndpointParameters,
        StopLimitOrderAPITranslateParametersParameters,
        StopLimitOrderAPIWrapResponseParameters,
    ]
):
    async def stop_limit_order(
        self,
        symbol: TSymbol,
        side: TSide,
        price: TPrice,
        size: TSize,
        trigger: TTrigger,
        *,
        extra_params: dict | None = None,
        request_params: dict | None = None,
    ) -> StopLimitOrderAPIResponse:
        extra_params = extra_params or {}
        request_params = request_params or {}
        endpoint = self._generate_endpoint(
            {
                "symbol": symbol,
                "side": side,
                "price": price,
                "size": size,
                "trigger": trigger,
                "extra_params": extra_params,
            }
        )
        parameters = self._translate_parameters(
            {
                "endpoint": endpoint,
                "symbol": symbol,
                "side": side,
                "price": price,
                "size": size,
                "trigger": trigger,
                "extra_params": extra_params,
            }
        )
        parameters = {**parameters, **extra_params}
        parameters = self._format_price(parameters, symbol)
        parameters = self._format_size(parameters, symbol)
        resp = await self.request(endpoint, parameters, **request_params)
        data = cast(dict, await self._decode_response(resp))
        order_id = self._extract_order_id(resp, data)
        return self._wrap_response({"order_id": order_id, "resp": resp, "data": data})


class StopLimitOrderAPIBuilder(
    OrderAPIBuilder[
        StopLimitOrderAPI,
        StopLimitOrderAPIGenerateEndpointParameters,
        StopLimitOrderAPITranslateParametersParameters,
        StopLimitOrderAPIWrapResponseParameters,
    ]
):
    def __init__(self):
        super(StopLimitOrderAPIBuilder, self).__init__(
            StopLimitOrderAPI, StopLimitOrderAPIResponse
        )
