from typing import Any

from abc import ABCMeta, abstractmethod


class Formatter(metaclass=ABCMeta):
    @abstractmethod
    def format(self, *args: Any, **kwargs: Any) -> str:
        raise NotImplementedError
