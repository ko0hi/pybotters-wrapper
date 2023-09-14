from typing import Any, NamedTuple, TypedDict, cast

from aiohttp.client import ClientResponse

from ...typedefs import TEndpoint, TPrice, TSide, TSize, TSymbol
from .order_api import OrderAPI
from .order_api_builder import OrderAPIBuilder


class LimitOrderAPIResponse(NamedTuple):
    order_id: str
    resp: ClientResponse
    data: Any = None


class LimitOrderAPIGenerateEndpointParameters(TypedDict):
    symbol: TSymbol
    side: TSide
    price: TPrice
    size: TSize
    extra_params: dict


class LimitOrderAPITranslateParametersParameters(TypedDict):
    endpoint: TEndpoint
    symbol: TSymbol
    side: TSide
    price: TPrice
    size: TSize
    extra_params: dict


class LimitOrderAPIWrapResponseParameters(TypedDict):
    order_id: str | None
    resp: ClientResponse
    data: Any


class LimitOrderAPI(
    OrderAPI[
        LimitOrderAPIResponse,
        LimitOrderAPIGenerateEndpointParameters,
        LimitOrderAPITranslateParametersParameters,
        LimitOrderAPIWrapResponseParameters,
    ]
):
    async def limit_order(
        self,
        symbol: TSymbol,
        side: TSide,
        price: TPrice,
        size: TSize,
        *,
        extra_params: dict | None = None,
        request_params: dict | None = None,
    ) -> LimitOrderAPIResponse:
        extra_params = extra_params or {}
        request_params = request_params or {}
        endpoint = self._generate_endpoint(
            {
                "symbol": symbol,
                "side": side,
                "price": price,
                "size": size,
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


class LimitOrderAPIBuilder(
    OrderAPIBuilder[
        LimitOrderAPI,
        LimitOrderAPIGenerateEndpointParameters,
        LimitOrderAPITranslateParametersParameters,
        LimitOrderAPIWrapResponseParameters,
    ]
):
    def __init__(self):
        super(LimitOrderAPIBuilder, self).__init__(LimitOrderAPI, LimitOrderAPIResponse)
