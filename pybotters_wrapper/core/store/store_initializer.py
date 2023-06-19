from __future__ import annotations

import asyncio
from abc import ABCMeta
from json import JSONDecodeError
from typing import Any, Literal, TypeAlias, Generic, Awaitable, NamedTuple

import aiohttp
import pybotters  # type: ignore

from ..typedefs import TDataStoreManager, TRequestMethod

TConfigKey: TypeAlias = Literal[
    "token",
    "token_public",
    "token_private",
    "ticker",
    "trades",
    "orderbook",
    "order",
    "position",
    "execution",
]
TUrl: TypeAlias = str
TRequiredParameters: TypeAlias = set[str]
TInitializerConfig: TypeAlias = dict[
    TConfigKey,
    tuple[TRequestMethod, TUrl, TRequiredParameters | None],
]


class InitializeRequestItem(NamedTuple):
    method: TRequestMethod
    url: str
    required_params: set | None = None

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

    class BinanceUSDSMStoreInitializer:
        def __init__(self, store: BinanceUSDSMDataStore):
            self._eprop = BinanceUSDSMExchangeProperty()
            self._initializer = StoreInitializer(store)
            self._initializer.register_token_config(
                "POST", f"{self._eprop.base_url}/fapi/v1/listenKey"
            )
            self._initializer.register_token_private_config(
                "POST", f"{self._eprop.base_url}/fapi/v1/listenKey"
            )
            self._initializer.register_orderbook_config(
                "GET", f"{self._eprop.base_url}/fapi/v1/depth", {"symbol"}
            )
            self._initializer.register_order_config(
                "GET", f"{self._eprop.base_url}/fapi/v1/openOrders"
            )
            self._initializer.register_position_config(
                "GET", f"{self._eprop.base_url}/fapi/v2/positionRisk"
            )

        ...

    """

    def __init__(
        self,
        store: TDataStoreManager,
        config: dict[
            TConfigKey,
            tuple[TRequestMethod, TUrl, TRequiredParameters | None],
        ] | None,
    ):
        self._store = store
        self._config = config

    async def initialize(
        self,
        aw_or_key_or_key_and_params_list: list[
            Awaitable[aiohttp.ClientResponse] | TUrl | tuple[TUrl, dict]
        ],
        client: pybotters.Client,
    ) -> None:
        """pybotters.DataStoreManagerの初期化メソッド（'initialize'）をラップするメソッド。

        - aw_or_key_or_key_and_params_listは以下のいずれかの形式で指定する
            - Awaitable[aiohttp.ClientResponse]
            - str
            - tuple[str, dict]
        - Awaitableはpybotters.DataStoreManager.initializeに直接渡されるので、任意のストアの初期化が可能
        - str（クエリパラメーターなし）およびtuple[str, dict]（クエリパラメーターあり）はself._configに登録されているもののみ有効
        """
        awaitables = [
            self._to_initialize_awaitable(a_or_n, client)
            for a_or_n in aw_or_key_or_key_and_params_list
        ]
        await self._initialize_with_validation(*awaitables)

    # aliases
    async def initialize_token(self, client: "pybotters.Client", **params: Any) -> None:
        """トークン発行用メソッド。BinanceやGMO CoinなどのAPIで使う。paramsは取引所別のAPIの
        クエリパラメーターで差分吸収は行わない。以下のinitializeメソッドも同様。
        """
        return await self.initialize([("token", params)], client)

    async def initialize_token_public(
        self, client: "pybotters.Client", **params: Any
    ) -> None:
        """publicトークン発行用メソッド。KuCoinのwebsocketなどで使う。"""
        return await self.initialize([("token_public", params)], client)

    async def initialize_token_private(
        self, client: "pybotters.Client", **params: Any
    ) -> None:
        """privateトークン発行用メソッド。Binanceのwebsocketなどで使う。"""
        return await self.initialize([("token_private", params)], client)

    async def initialize_ticker(
        self, client: "pybotters.Client", **params: Any
    ) -> None:
        """TickerNormalizedStore初期化用メソッド。一応用意しているが多分使うことはない。"""
        return await self.initialize([("ticker", params)], client)

    async def initialize_trades(
        self, client: "pybotters.Client", **params: Any
    ) -> None:
        """TradesNormalizedStore初期化用メソッド。"""
        return await self.initialize([("trades", params)], client)

    async def initialize_orderbook(
        self, client: "pybotters.Client", **params: Any
    ) -> None:
        """OrderbookNormalizedStore初期化用メソッド。"""
        return await self.initialize([("orderbook", params)], client)

    async def initialize_order(self, client: "pybotters.Client", **params: Any) -> None:
        """OrderNormalizedStore初期化用メソッド。"""
        return await self.initialize([("order", params)], client)

    async def initialize_execution(
        self, client: "pybotters.Client", **params: Any
    ) -> None:
        """ExecutionNormalizedStore初期化用メソッド。"""
        return await self.initialize([("execution", params)], client)

    async def initialize_position(
        self, client: "pybotters.Client", **params: Any
    ) -> None:
        """PositionNormalizedStore初期化用メソッド。"""
        return await self.initialize([("position", params)], client)

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
        """self._configからkeyに対応するInitializeRequestItemを取得する。"""
        if key not in self._config:
            raise ValueError(
                f"Unsupported endpoint: {key}, "
                f"available endpoints are {list(self._config.keys())}",
            )
        return InitializeRequestItem(*self._config[key])

    def _to_initialize_awaitable_from_config(
        self,
        client: pybotters.Client,
        key: str,
        **params: Any,
    ) -> Awaitable:
        params = dict(params)
        item = self._get_initialize_request_item(key)
        self._validate_required_params(item, params)
        return self._request_with_initialize_request_item(client, item, params)

    async def _initialize_with_validation(self, *aws: Awaitable):
        # awaitableの結果をvalidation時に参照したいのでTaskで囲む
        aws_tasks: list[asyncio.Task] = [asyncio.create_task(aw) for aw in aws]  # type: ignore
        try:
            await self._store.initialize(*aws_tasks)
        except AttributeError:
            # initializeはDataStoreManagerのメソッドではなく、各実装クラスレベルでのメソッド
            # bitbankDataStoreなど実装がない
            pass
        finally:
            # APIレスポンスが成功していたかチェック
            # _store.initializeの中でas_completedが使われているので必ず終了している。
            for task in aws_tasks:
                await self._validate_initialize_response(task)

    @classmethod
    def _request_with_initialize_request_item(
        cls,
        client: pybotters.Client,
        item: InitializeRequestItem,
        params_or_data: dict | None = None,
    ) -> Awaitable:
        method = item.method
        url = item.url
        kwargs: dict[str, Any] = dict(method=method, url=url)
        if params_or_data:
            kwargs["params" if method == "GET" else "data"] = params_or_data
        return client.request(**kwargs)

    @classmethod
    def _validate_required_params(
        cls, item: InitializeRequestItem, params: dict | None
    ):
        if item.required_params:
            if params is None:
                raise ValueError(
                    f"Missing required parameters for {item.url}: {item.required_params}"
                )

            missing_params = item.required_params.difference(params.keys())
            if len(missing_params):
                raise ValueError(
                    f"Missing required parameters for {item.url}: {missing_params}"
                )

    @classmethod
    async def _validate_initialize_response(cls, task: asyncio.Task):
        result: aiohttp.ClientResponse = task.result()
        if result.status != 200:
            try:
                data = await result.json()
            except JSONDecodeError:
                data = None
            raise RuntimeError(f"Initialization request failed: {result.url} {data}")
