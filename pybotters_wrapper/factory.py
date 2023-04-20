from typing import Literal

import pybotters

from .core import APIClient, WebSocketConnection
from .core.websocket_connection import WebsocketOnReconnectionCallback, WsHandler



def create_client(
    apis: dict[str, list[str]] | str | None = None,
    base_url: str = "",
    **kwargs: any,
) -> pybotters.Client:
    return pybotters.Client(apis, base_url, **kwargs)


def create_api(exchange: str, client: pybotters.Client) -> APIClient:
    return _EXCHANGE2API[exchange](client)


def create_websocket_connection(
    endpoint: str,
    send: dict | list[dict] | str,
    hdlr: WsHandler | list[WsHandler],
    send_type: Literal["json", "str", "byte"] = "json",
    hdlr_type: Literal["json", "str", "byte"] = "json",
) -> WebSocketConnection:
    return WebSocketConnection(endpoint, send, hdlr, send_type, hdlr_type)


async def create_and_connect_websocket_connection(
    client: pybotters.Client,
    endpoint: str,
    send: dict | list[dict] | str,
    hdlr: WsHandler | list[WsHandler],
    send_type: Literal["json", "str", "byte"] = "json",
    hdlr_type: Literal["json", "str", "byte"] = "json",
    auto_reconnect: bool = False,
    on_reconnection: WebsocketOnReconnectionCallback | None = None,
    **kwargs,
) -> WebSocketConnection:
    conn = create_websocket_connection(endpoint, send, hdlr, send_type, hdlr_type)
    return await conn.connect(client, auto_reconnect, on_reconnection, **kwargs)
