import asyncio

import pybotters.store

from .helper import generate_attribute_checker, execute_fn


class WaitStoreMixin:
    __store: pybotters.store.DataStore
    __break: bool
    __wait_task: asyncio.Task

    _checker = generate_attribute_checker("init_wait_store", "__store")

    def init_wait_store(self, store: pybotters.store.DataStore):
        self.__store = store
        self.__break = False
        self.__wait_task = asyncio.create_task(self.__run_wait_task())

    async def __run_wait_task(self):
        # 使用するDataStoreのwaitをそれぞれ監視してキューで結果を取得する
        is_aw_on_before = asyncio.iscoroutinefunction(self._on_wait_before)
        is_aw_on_first = asyncio.iscoroutinefunction(self._on_wait_first)
        is_aw_on_wait = asyncio.iscoroutinefunction(self._on_wait)
        is_aw_on_after = asyncio.iscoroutinefunction(self._on_wait_after)

        await execute_fn(self._on_wait_before, is_aw_on_before)

        await self.__store.wait()
        await execute_fn(self._on_wait_first, is_aw_on_first)

        while True:
            await self.__store.wait()
            await execute_fn(self._on_wait, is_aw_on_wait)

            if self.__break:
                break

        await execute_fn(self._on_wait_after, is_aw_on_after)

    def _on_wait_before(self):
        ...

    def _on_wait_first(self):
        ...

    def _on_wait(self):
        ...

    def _on_wait_after(self):
        ...

    @_checker
    def set_break(self):
        self.__break = True

    @_checker
    def stop(self):
        if self.__wait_task is not None and not self.__wait_task.done():
            self.__wait_task.cancel()

    @property
    def wait_store(self):
        return self.__store

    @property
    def wait_task(self):
        return self.__wait_task


class WaitMultipleStoreMixin:
    __stores: list[pybotters.store.DataStore]
    __queue: asyncio.Queue
    __break: bool
    __wait_tasks: list[asyncio.Task]

    _checker = generate_attribute_checker("init_wait_multiple_storse",
                                          "__store")

    def init_wait_multiple_stores(self, *stores: pybotters.store.DataStore):
        self.__stores = stores
        self.__break = False
        self.__wait_tasks = [asyncio.create_task(self.__run_wait_task_one(s))
                             for s in stores]

    async def __run_wait_task_one(self, store: pybotters.store.DataStore):
        while True:
            await store.wait()
            self.__queue.put_nowait(store)

    async def __run_wait_task(self):
        # 使用するDataStoreのwaitをそれぞれ監視してキューで結果を取得する
        is_aw_on_before = asyncio.iscoroutinefunction(self._on_wait_before)
        is_aw_on_first = asyncio.iscoroutinefunction(self._on_wait_first)
        is_aw_on_wait = asyncio.iscoroutinefunction(self._on_wait)
        is_aw_on_after = asyncio.iscoroutinefunction(self._on_wait_after)

        await execute_fn(self._on_wait_before, is_aw_on_before)

        store = await self.__queue.get()
        await execute_fn(self._on_wait_first, is_aw_on_first, store)

        while True:
            store = await self.__queue.get()
            await execute_fn(self._on_wait, is_aw_on_wait, store)

            if self.__break:
                break

        await execute_fn(self._on_wait_after, is_aw_on_after)

    def _on_wait_before(self):
        ...

    def _on_wait_first(self, store: pybotters.store.DataStore):
        ...

    def _on_wait(self, store: pybotters.store.DataStore):
        ...

    def _on_wait_after(self):
        ...

    @_checker
    def set_break(self):
        self.__break = True

    @_checker
    def stop(self):
        if self.__wait_tasks is not None:
            for t in self.__wait_tasks:
                if not t.done():
                    t.cancel()

    @property
    def wait_stores(self):
        return self.__stores

    @property
    def wait_tasks(self):
        return self.__wait_tasks
