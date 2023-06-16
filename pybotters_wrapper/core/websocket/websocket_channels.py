from __future__ import annotations

from typing import Any, Literal, Generic, Union, TypeVar, NamedTuple, cast

TChannelName = TypeVar("TChannelName")


class SubscribeItem(NamedTuple):
    endpoint: str
    parameter: Any


class WebSocketChannels(Generic[TChannelName]):
    """Websocketのチャンネル購読リクエストを生成するクラス。

    - 取引所が提供する各チャンネル用のメソッドを提供する
    - NormalizedDataStoreに対応するチャンネルメソッド（`ticker`, `trades`, `orderbook`,
    `order`, `execution`, and `position`）を提供する

    """

    _ENDPOINT: str | None = None

    def channel(
        self,
        name: Union[
            TChannelName,
            Literal["ticker", "trades", "orderbook", "order", "execution", "position"],
        ],
        **params,
    ) -> SubscribeItem | list[SubscribeItem]:
        try:
            method = getattr(self, cast(str, name))
        except AttributeError as e:
            raise AttributeError(f"Unsupported channel: {name}")
        parameter = method(**params)
        if isinstance(parameter, list):
            subscribe_items = []
            for _parameter in parameter:
                endpoint = self._get_endpoint(_parameter)
                parameter_in_template = self._parameter_template(_parameter)
                subscribe_items.append(SubscribeItem(endpoint, parameter_in_template))
            return subscribe_items
        else:
            endpoint = self._get_endpoint(parameter)
            parameter_in_template = self._parameter_template(parameter)
            return SubscribeItem(endpoint, parameter_in_template)

    def ticker(self, symbol: str, **kwargs) -> dict | str | list[dict | str]:
        """TickerStore用のチャンネルをsubscribeする"""
        raise NotImplementedError

    def trades(self, symbol: str, **kwargs) -> dict | str | list[dict | str]:
        """TradesStore用のチャンネルをsubscribeする"""
        raise NotImplementedError

    def orderbook(self, symbol: str, **kwargs) -> dict | str | list[dict | str]:
        """OrderbookStore用のチャンネルをsubscribeする"""
        raise NotImplementedError

    def order(self, **kwargs) -> dict | str | list[dict | str]:
        """OrderStore用のチャンネルをsubscribeする"""
        raise NotImplementedError

    def execution(self, **kwargs) -> dict | str | list[dict | str]:
        """ExecutionStore用のチャンネルをsubscribeする"""
        raise NotImplementedError

    def position(self, **kwargs) -> dict | str | list[dict | str]:
        """PositionStore用のチャンネルをsubscribeする"""
        raise NotImplementedError

    def _get_endpoint(self, parameter: str | dict[str, Any]) -> str:
        assert self._ENDPOINT is not None
        return self._ENDPOINT

    def _parameter_template(self, parameter: str | dict[str, Any]) -> str | dict[str, Any]:
        return parameter

