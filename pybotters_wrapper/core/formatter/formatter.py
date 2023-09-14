from abc import ABCMeta, abstractmethod
from typing import Any


class Formatter(metaclass=ABCMeta):
    @abstractmethod
    def format(self, *args: Any, **kwargs: Any) -> str:
        raise NotImplementedError
