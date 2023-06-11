from __future__ import annotations

import asyncio
import uuid
from typing import (
    Any,
    Callable,
    Generic,
    Hashable,
    Iterator,
    Literal,
    Type,
    TypeVar,
    TypedDict,
    Union,
)

import pybotters
from pybotters.store import (
    DataStore,
    Item,
    StoreChange,
    StoreStream,
    ClientWebSocketResponse,
)

TNormalizedItem = TypeVar("TNormalizedItem", bound=TypedDict)


class NormalizedDataStore(Generic[TNormalizedItem]):
    _BASE_STORE_NAME: str | None = None
    _NAME: str | None = None
    _KEYS: list[str] | None = []
    _NORMALIZED_ITEM_CLASS: Type[TNormalizedItem] | None = None

    def __init__(
        self,
        store: DataStore | None,
        *,
        mapper: Union[
            dict[str, str | Callable[[DataStore, str, dict, dict], Any]],
            Callable[[DataStore, str, dict, dict], Any],
            None,
        ] = None,
        name: str | None = None,
        keys: list[str] | None = None,
        data: list[Item] | None = None,
        auto_cast: bool = False,
        target_operations: tuple[Literal["insert", "update", "delete"], ...]
        | None = None,
        on_wait: Callable[[NormalizedDataStore], None] | None = None,
        on_msg: Callable[[NormalizedDataStore, Item], None] | None = None,
        on_watch_get_operation: Callable[[StoreChange], str | None] | None = None,
        on_watch_make_item: Callable[[TNormalizedItem, StoreChange], dict]
        | None = None,
    ):
        # 参照元のデータストア
        self._base_store: DataStore = store
        # 正規化したデータストア
        self._normalized_store: DataStore = DataStore(
            name or self._NAME or self._base_store.name,
            keys or self._KEYS,
            data or [],
            auto_cast=auto_cast,
        )

        self._mapper = mapper
        self._target_operations = target_operations or ("insert", "update", "delete")

        self._wait_task: asyncio.Task | None = None
        self._watch_task: asyncio.Task | None = None
        self._queue_task: asyncio.Task | None = None
        self._queue: pybotters.WebSocketQueue | None = None

        self._on_wait_fn = on_wait
        self._on_msg_fn = on_msg
        self._on_watch_get_operation = on_watch_get_operation
        self._on_watch_make_item = on_watch_make_item

    def start(self) -> NormalizedDataStore:
        """元ストアとの同期を開始する"""
        if self._base_store is not None:
            self._wait_task = asyncio.create_task(self._wait_store())
            self._watch_task = asyncio.create_task(self._watch_store())
        else:
            self._wait_task = None
            self._watch_task = None
        self._queue = pybotters.WebSocketQueue()
        self._queue_task = asyncio.create_task(self._wait_msg())
        return self

    async def close(self) -> None:
        if self._wait_task:
            try:
                self._wait_task.cancel()
                await self._wait_task
            except asyncio.CancelledError:
                ...

        if self._watch_task:
            try:
                self._watch_task.cancel()
                await self._watch_task
            except asyncio.CancelledError:
                ...

        if self._queue_task:
            try:
                self._queue_task.cancel()
                await self._queue_task
            except asyncio.CancelledError:
                ...

    def synchronize(self) -> None:
        """元ストアと強制同期する"""
        self._clear()
        items = []
        for i in self._base_store.find():
            item = {
                **self._normalize(self._base_store, "insert", {}, i),
                "info": {"data": i, "source": {}},
            }
            items.append(item)
        self._insert(items)

    def _onmessage(self, msg: "Item", ws: "ClientWebSocketResponse") -> None:
        if self._queue is not None:
            self._queue.onmessage(msg, ws)

    async def _wait_store(self) -> None:
        while True:
            await self._base_store.wait()
            self._on_wait()

    def _on_wait(self) -> None:
        if self._on_wait_fn is not None:
            self._on_wait_fn(self)

    async def _wait_msg(self) -> None:
        if self._queue is not None:
            async for msg in self._queue.iter_msg():
                self._on_msg(msg)

    def _on_msg(self, msg: "Item") -> None:
        if self._on_msg_fn is not None:
            self._on_msg_fn(self, msg)

    async def _watch_store(self) -> None:
        with self._base_store.watch() as stream:
            async for change in stream:
                self._on_watch(change)

    def _on_watch(self, change: "StoreChange") -> None:
        op = self._get_operation(change)
        if op is not None:
            # StoreChange.[data|source]はdeep copyされたものが入っている
            normalized_data = self._normalize(
                change.store, change.operation, change.source, change.data
            )
            item = self._make_item(normalized_data, change)
            self._check_operation(op)
            op_fn = getattr(self, "_" + op)
            op_fn([item])

    def _normalize(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ) -> "TNormalizedItem":
        assert self._mapper is not None
        if callable(self._mapper):
            return self._mapper(store, operation, source, data)
        elif isinstance(self._mapper, dict):
            values = {}
            for k, value_or_fn in self._mapper.items():
                if isinstance(value_or_fn, str):
                    values[k] = value_or_fn
                elif callable(value_or_fn):
                    values[k] = value_or_fn(store, operation, source, data)
                else:
                    raise TypeError(f"Unsupported dict mapper: {self._mapper}")
            return self._itemize(**values)
        else:
            raise TypeError(f"Unsupported mapper: {self._mapper}")

    def _itemize(self, *args, **kwargs) -> "TNormalizedItem":
        assert self._NORMALIZED_ITEM_CLASS is not None
        return self._NORMALIZED_ITEM_CLASS(*args, **kwargs)

    def _get_operation(self, change: "StoreChange") -> str | None:
        if self._on_watch_get_operation is not None:
            return self._on_watch_get_operation(change)
        else:
            return change.operation

    def _make_item(
        self, normalized_item: "TNormalizedItem", change: "StoreChange"
    ) -> "Item":
        # ストアに格納するアイテムとしてはchange.sourceは不要かもしれないが、watchした際に元のitemの
        # sourceをたどりたい場合がありうるので付帯させる
        if self._on_watch_make_item is not None:
            return self._on_watch_make_item(normalized_item, change)
        else:
            return {
                **normalized_item,
                "info": {"data": change.data, "source": change.source},
            }

    def _check_operation(self, operation: str):
        if operation not in self._target_operations:
            raise RuntimeError(
                f"Unsupported operation '{operation}' for {self.__class__.__name__}"
            )

    # ラップメソッド
    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"({self._base_store.__class__.__module__}.{self._base_store.__class__.__name__})"
        )

    def __len__(self) -> int:
        return self._normalized_store.__len__()

    def __iter__(self) -> Iterator[Item]:
        return self._normalized_store.__iter__()

    def __reversed__(self) -> Iterator[Item]:
        return self._normalized_store.__reversed__()

    @staticmethod
    def _hash(item: dict[str, Hashable]) -> int:
        return DataStore._hash(item)

    @staticmethod
    def _cast_item(item: dict[str, Hashable]) -> None:
        return DataStore._cast_item(item)

    def _insert(self, data: list[Item]) -> None:
        return self._normalized_store._insert(data)

    def _update(self, data: list[Item]) -> None:
        return self._normalized_store._update(data)

    def _delete(self, data: list[Item]) -> None:
        return self._normalized_store._delete(data)

    def _remove(self, uuids: list[uuid.UUID]) -> None:
        return self._normalized_store._remove(uuids)

    def _clear(self) -> None:
        return self._normalized_store._clear()

    def _sweep_with_key(self) -> None:
        return self._normalized_store._sweep_with_key()

    def _sweep_without_key(self) -> None:
        return self._normalized_store._sweep_without_key()

    def get(self, item: Item) -> Item | None:
        return self._normalized_store.get(item)

    def _pop(self, item: Item) -> Item | None:
        return self._normalized_store.get(item)

    def find(self, query: Item | None = None) -> list[Item]:
        return self._normalized_store.find(query)

    def _find_with_uuid(self, query: Item | None = None) -> dict[uuid.UUID, Item]:
        return self._normalized_store._find_with_uuid(query)

    def _find_and_delete(self, query: Item | None = None) -> list[Item]:
        return self._normalized_store._find_and_delete(query)

    def _set(self, data: list[Item] | None = None) -> None:
        return self._normalized_store._set(data)

    async def wait(self) -> list[Item]:
        return await self._normalized_store.wait()

    def _put(self, operation: str, source: Item | None, item: Item) -> None:
        return self._normalized_store._put(operation, source, item)

    def watch(self) -> "StoreStream":
        return self._normalized_store.watch()
