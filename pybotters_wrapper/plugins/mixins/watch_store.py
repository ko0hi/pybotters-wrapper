import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pybotters.store import DataStore


import pybotters.store

from .helper import execute_fn, generate_attribute_checker


def _unwrap(
    change: pybotters.store.StoreChange,
) -> tuple[pybotters.store.DataStore, str, dict, dict]:
    return (
        change.store,
        change.operation,
        change.source,
        change.data,
    )


class WatchStoreMixin:
    __store: pybotters.store.DataStore
    __break: bool
    __watch_task: asyncio.Task

    _checker = generate_attribute_checker("init_watch_store", "_WatchStoreMixin__store")

    def init_watch_store(self, store: pybotters.store.DataStore):
        self.__store = store
        self.__break = False
        self.__watch_task = asyncio.create_task(self.__run_watch_task())

    async def __run_watch_task(self):
        """watch監視"""
        is_aw_on_before = asyncio.iscoroutinefunction(self._on_watch_before)
        is_aw_on_first = asyncio.iscoroutinefunction(self._on_watch_first)
        is_aw_on_watch = asyncio.iscoroutinefunction(self._on_watch)
        is_aw_on_after = asyncio.iscoroutinefunction(self._on_watch_after)

        await execute_fn(self._on_watch_before, is_aw_on_before)

        with self.__store.watch() as stream:
            c1: pybotters.store.StoreChange = await stream.get()
            await execute_fn(self._on_watch_first, is_aw_on_first, *_unwrap(c1))
            await execute_fn(self._on_watch, is_aw_on_watch, *_unwrap(c1))
            if self.__break:
                await execute_fn(self._on_watch_after, is_aw_on_after)
                return

            async for c in stream:
                await execute_fn(self._on_watch, is_aw_on_watch, *_unwrap(c))

                if self.__break:
                    break

        await execute_fn(self._on_watch_after, is_aw_on_after)

    def _on_watch_before(self):
        ...

    def _on_watch_first(
        self, store: DataStore, operation: str, source: dict, data: dict
    ):
        ...

    def _on_watch(self, store: DataStore, operation: str, source: dict, data: dict):
        ...

    def _on_watch_after(self):
        ...

    @_checker
    def set_break(self):
        self.__break = True

    @_checker
    def stop(self):
        if self.__watch_task is not None and not self.__watch_task.done():
            self.__watch_task.cancel()

    @property
    def watch_store(self):
        return self.__store

    @property
    def watch_task(self):
        return self.__watch_task


class WatchMultipleStoreMixin:
    __stores: list[DataStore]
    __queue: asyncio.Queue
    __break: bool
    __watch_tasks: list[asyncio.Task]

    _checker = generate_attribute_checker(
        "init_watch_multiple_stores", "_WatchMultipleStoreMixin__store"
    )

    def init_watch_multiple_stores(self, *stores: DataStore):
        self.__stores = list(stores)
        self.__break = False
        self.__watch_tasks = [
            asyncio.create_task(self.__run_watch_task_one(s)) for s in stores
        ]

    async def __run_watch_task_one(self, store: DataStore):
        with store.watch() as stream:
            async for change in stream:
                self.__queue.put_nowait(change)

    async def __run_watch_task(self):
        """watch監視"""
        is_aw_on_before = asyncio.iscoroutinefunction(self._on_watch_before)
        is_aw_on_first = asyncio.iscoroutinefunction(self._on_watch_first)
        is_aw_on_watch = asyncio.iscoroutinefunction(self._on_watch)
        is_aw_on_after = asyncio.iscoroutinefunction(self._on_watch_after)

        await execute_fn(self._on_watch_before, is_aw_on_before)

        change1: pybotters.store.StoreChange = await self.__queue.get()
        await execute_fn(self._on_watch_first, is_aw_on_first, *_unwrap(change1))
        await execute_fn(self._on_watch, is_aw_on_watch, *_unwrap(change1))

        if self.__break:
            await execute_fn(self._on_watch_after, is_aw_on_after)
            return

        while True:
            c: pybotters.store.StoreChange = await self.__queue.get()
            await execute_fn(self._on_watch, is_aw_on_watch, *_unwrap(c))

            if self.__break:
                break

        await execute_fn(self._on_watch_after, is_aw_on_after)

    def _on_watch_before(self) -> None:
        ...

    def _on_watch_first(
        self, store: DataStore, operation: str, source: dict, data: dict
    ) -> None:
        ...

    def _on_watch(
        self, store: DataStore, operation: str, source: dict, data: dict
    ) -> None:
        ...

    def _on_watch_after(self) -> None:
        ...

    @_checker
    def set_break(self) -> None:
        self.__break = True

    @_checker
    def stop(self) -> None:
        if self.__watch_tasks is not None:
            for t in self.__watch_tasks:
                if not t.done():
                    t.cancel()

    @property
    def watch_stores(self) -> list[DataStore]:
        return self.__stores

    @property
    def watch_tasks(self):
        return self.__watch_tasks
