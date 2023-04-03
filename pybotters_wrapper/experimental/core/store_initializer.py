from __future__ import annotations

import asyncio
from abc import ABCMeta
from typing import Generic, Awaitable, NamedTuple, Optional

import aiohttp
import pybotters

from .._typedefs import TDataStoreManager, RequsetMethod


class InitializeRequestItem(NamedTuple):
    method: RequsetMethod
    url: str
    required_params: set = None

    @classmethod
    def from_tuple(cls, item: tuple):
        return cls.init_with_validation(item)

    @classmethod
    def init_with_validation(cls, item: tuple) -> InitializeRequestItem:
        err_msg = f"Unsupported InitializeRequestItem: {item}"
        try:
            item = cls(*item)
        except TypeError as e:
            raise TypeError(err_msg)
        else:
            if not (
                isinstance(item.method, str)
                and isinstance(item.url, str)
                and (
                    item.required_params is None
                    or isinstance(item.required_params, set)
                )
            ):
                raise TypeError(err_msg)
            return item


class StoreInitializer(Generic[TDataStoreManager], metaclass=ABCMeta):
    """pybotters.DataStoreManagerの初期化メソッド（'initialize'）をラップするクラス。

    - `NormalizedDataStore`の初期化エイリアスを提供する
    - pybottersでサポートされている任意のストアの初期化も可能

    .. code-block:: python

    from pybotters.models.binance import BinanceUSDSMDataStore

    class BinanceUSDSMStoreInitializer(StoreInitializer[BinanceUSDSMDataStore]):
        _DEFAULT_INITIALIZE_CONFIG = {
            "token": ("POST", "https://fapi.binance.com/fapi/v1/listenKey", None),
            "token_private": ("POST", "https://fapi.binance.com/fapi/v1/listenKey", None),
            "orderbook": ("GET", "https://fapi.binance.com/fapi/v1/depth", {"symbol"}),
            "order": ("GET", "https://fapi.binance.com/fapi/v1/openOrders", None),
            "position": ("GET", "https://fapi.binance.com/fapi/v2/positionRisk", None),
        }

    """

    _DEFAULT_INITIALIZE_CONFIG: dict[str, InitializeRequestItem] = {}

    def __init__(
        self,
        store: TDataStoreManager,
        config: dict[str, tuple[str, str, Optional[dict]]] = None,
    ):
        self._store: TDataStoreManager = store
        self._config: dict[str, tuple[str, str, Optional[dict]]] = (
            config or self._DEFAULT_INITIALIZE_CONFIG
        )

    async def initialize(
        self,
        aw_or_key_or_key_and_params_list: list[
            Awaitable[aiohttp.ClientResponse] | str | tuple[str, dict]
        ],
        client: pybotters.Client,
    ):
        awaitables = [
            self._to_initialize_awaitable(a_or_n, client)
            for a_or_n in aw_or_key_or_key_and_params_list
        ]
        await self._initialize_with_validation(*awaitables)

    # aliases
    async def initialize_token(self, client: "pybotters.Client", **params):
        return await self.initialize([("token", params)], client)

    async def initialize_token_public(self, client: "pybotters.Client", **params):
        return await self.initialize([("token_public", params)], client)

    async def initialize_token_private(self, client: "pybotters.Client", **params):
        return await self.initialize([("token_private", params)], client)

    async def initialize_ticker(self, client: "pybotters.Client", **params):
        return await self.initialize([("ticker", params)], client)

    async def initialize_trades(self, client: "pybotters.Client", **params):
        return await self.initialize([("trades", params)], client)

    async def initialize_orderbook(self, client: "pybotters.Client", **params):
        return await self.initialize([("orderbook", params)], client)

    async def initialize_order(self, client: "pybotters.Client", **params):
        return await self.initialize([("order", params)], client)

    async def initialize_execution(self, client: "pybotters.Client", **params):
        return await self.initialize([("execution", params)], client)

    async def initialize_position(self, client: "pybotters.Client", **params):
        return await self.initialize([("position", params)], client)

    def register_config(
        self, key: str, method: str, url: str, required_params: set | None = None
    ):
        self._config[key] = InitializeRequestItem(method, url, required_params)

    def register_token_config(
        self, method: str, url: str, requred_params: set | None = None
    ):
        self.register_config("token", method, url, requred_params)

    def register_token_public_config(
        self, method: str, url: str, requred_params: set | None = None
    ):
        self.register_config("token_public", method, url, requred_params)

    def register_token_private_config(
        self, method: str, url: str, requred_params: set | None = None
    ):
        self.register_config("token_private", method, url, requred_params)

    def register_ticker_config(
        self, method: str, url: str, requred_params: set | None = None
    ):
        self.register_config("ticker", method, url, requred_params)

    def register_trades_config(
        self, method: str, url: str, requred_params: set | None = None
    ):
        self.register_config("trades", method, url, requred_params)

    def register_orderbook_config(
        self, method: str, url: str, requred_params: set | None = None
    ):
        self.register_config("orderbook", method, url, requred_params)

    def register_order_config(
        self, method: str, url: str, requred_params: set | None = None
    ):
        self.register_config("order", method, url, requred_params)

    def register_execution_config(
        self, method: str, url: str, requred_params: set | None = None
    ):
        self.register_config("execution", method, url, requred_params)

    def register_position_config(
        self, method: str, url: str, requred_params: set | None = None
    ):
        self.register_config("position", method, url, requred_params)

    def _to_initialize_awaitable(
        self,
        aw_or_key_or_key_and_params: Awaitable[aiohttp.ClientResponse]
        | str
        | tuple[str, dict],
        client: pybotters.Client,
    ) -> Awaitable[aiohttp.ClientResponse]:
        """store.initializeに渡されるAwaitableに変換する。"""
        if isinstance(aw_or_key_or_key_and_params, Awaitable):
            # pybottersそのままの形式
            return aw_or_key_or_key_and_params
        elif isinstance(aw_or_key_or_key_and_params, str):
            # config（引数なし）
            return self._to_initialize_awaitable_from_config(
                client, aw_or_key_or_key_and_params
            )
        elif (
            isinstance(aw_or_key_or_key_and_params, tuple)
            and len(aw_or_key_or_key_and_params) == 2
            and isinstance(aw_or_key_or_key_and_params[0], str)
            and isinstance(aw_or_key_or_key_and_params[1], dict)
        ):
            # config（引数あり）
            return self._to_initialize_awaitable_from_config(
                client, aw_or_key_or_key_and_params[0], **aw_or_key_or_key_and_params[1]
            )
        else:
            raise TypeError(f"Invalid input: {aw_or_key_or_key_and_params}")

    def _get_initialize_request_item(self, key: str) -> InitializeRequestItem:
        if key not in self._config:
            raise ValueError(
                f"Unsupported endpoint: {key}, "
                f"available endpoints are {list(self._config.keys())}",
            )
        return InitializeRequestItem(*self._config[key])

    def _request_with_initialize_request_item(
        self,
        client: "pybotters.Client",
        item: InitializeRequestItem,
        params_or_data: Optional[dict] = None,
    ) -> Awaitable:
        method = item.method
        url = item.url
        params = dict(method=method, url=url)
        params["params" if method == "GET" else "data"] = params_or_data
        return client.request(**params)

    def _to_initialize_awaitable_from_config(
        self,
        client: pybotters.Client,
        key: str,
        **params: dict,
    ) -> Awaitable:
        params = dict(params)
        item = self._get_initialize_request_item(key)
        self._validate_required_params(item, params)
        return self._request_with_initialize_request_item(client, item, params)

    def _validate_required_params(
        self, item: InitializeRequestItem, params: dict | None
    ):
        if item.required_params:
            if params is None:
                raise f"Missing required parameters for {item.url}: {item.required_params}"

            missing_params = item.required_params.difference(params.keys())
            if len(missing_params):
                raise ValueError(
                    f"Missing required parameters for {item.url}: {missing_params}"
                )

    async def _validate_initialize_response(self, task: asyncio.Task):
        result: aiohttp.ClientResponse = task.result()

        if not isinstance(result, aiohttp.ClientResponse):
            raise TypeError(
                f"Unsupported response type for initialize request: {result}"
            )

        if result.status != 200:
            try:
                data = await result.json()
            except Exception:
                data = None
            raise RuntimeError(f"Initialization request failed: {result.url} {data}")

    async def _initialize_with_validation(self, *aws: list[Awaitable]):
        # awaitableの結果をvalidation時に参照したいのでTaskで囲む
        aws_tasks = [asyncio.create_task(aw) for aw in aws]
        try:
            await self._store.initialize(*aws_tasks)
        except AttributeError:
            # initializeはDataStoreManagerのメソッドではなく、各実装クラスレベルでのメソッド
            # bitbankDataStoreなど実装がない
            pass
        finally:
            # APIレスポンスが成功していたかチェック
            for task in aws_tasks:
                await self._validate_initialize_response(task)
