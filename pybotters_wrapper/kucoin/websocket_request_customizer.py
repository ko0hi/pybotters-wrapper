from typing import Type

import pybotters

from ..core import WebSocketRequestCustomizer
from .endpoint_resolver import KuCoinEndpointResolver


class KuCoinWebSocketRequestCustomizer(WebSocketRequestCustomizer):
    _EXCHANGE: str

    def __init__(self, client: pybotters.Client | None = None):
        super(KuCoinWebSocketRequestCustomizer, self).__init__(client)
        self._endpoint_resolver: KuCoinEndpointResolver | None = None
        if client is not None:
            self._endpoint_resolver = self._init_resolver()

    def customize(
        self, endpoint: str, request_list: list[dict | str]
    ) -> tuple[str, list[dict | str]]:
        assert self._endpoint_resolver is not None
        dynamic_endpoint = self._endpoint_resolver.resolve()
        return dynamic_endpoint, request_list

    def set_client(self, client: pybotters.Client) -> WebSocketRequestCustomizer:
        super().set_client(client)
        self._endpoint_resolver = self._init_resolver()
        return self

    def _init_resolver(self) -> KuCoinEndpointResolver:
        assert self._client is not None
        return KuCoinEndpointResolver(self._client, self._EXCHANGE)


def create_websocket_request_customizer(
    exchange: str,
) -> Type[KuCoinWebSocketRequestCustomizer]:
    class _KuCoinWebSocketRequestCustomizer(KuCoinWebSocketRequestCustomizer):
        _EXCHANGE = exchange

    return _KuCoinWebSocketRequestCustomizer
