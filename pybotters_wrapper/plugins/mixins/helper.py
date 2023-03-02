import asyncio
from typing import Callable


def generate_attribute_checker(init_method_name: str, attr: str) -> Callable:
    def _decorator(fn):
        def _wrapper(self, *args, **kwargs):
            try:
                getattr(self, attr)
            except AttributeError:
                raise RuntimeError(
                    f"Initialize attributes of your {self.__class__.__name__} "
                    f"instance with {init_method_name}()"
                )
            return fn(self, *args, **kwargs)

        return _wrapper

    return _decorator


async def execute_fn(fn: Callable, is_awaitable: bool = None, *args) -> any:
    if is_awaitable is None:
        is_awaitable = asyncio.iscoroutinefunction(fn)
    if is_awaitable:
        return await fn(*args)
    else:
        return fn(*args)
