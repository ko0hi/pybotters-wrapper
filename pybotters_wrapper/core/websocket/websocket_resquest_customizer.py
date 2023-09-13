from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Callable, Generic, TypeVar

import pybotters

TRequest = TypeVar("TRequest")


class WebSocketRequestCustomizer(Generic[TRequest], metaclass=ABCMeta):
    def __init__(self, client: pybotters.Client = None):
        self._client = client

    def __call__(
        self, endpoint: str, request_list: list[TRequest]
    ) -> tuple[str, list[TRequest]]:
        return self.customize(endpoint, request_list)

    def set_client(self, client: pybotters.Client) -> WebSocketRequestCustomizer:
        self._client = client
        return self

    @abstractmethod
    def customize(
        self, endpoint: str, request_list: list[TRequest]
    ) -> tuple[str, list[TRequest]]:
        return endpoint, request_list

    @classmethod
    def compress_request_list(
        cls, request_list: list[TRequest], hash_fn: Callable = str
    ) -> list[TRequest]:
        compressed = []
        for req in request_list:
            req_str = hash_fn(req)
            if req_str not in compressed:
                compressed.append(req)
        return compressed


class WebSocketDefaultRequestCustomizer(WebSocketRequestCustomizer):
    def customize(
        self, endpoint: str, request_list: list[dict | str]
    ) -> tuple[str, list[dict | str]]:
        return endpoint, self.compress_request_list(request_list)

    @classmethod
    def compress_request_list(
        cls, request_list: list[dict | str], hash_fn: Callable = str
    ) -> list[dict | str]:
        compressed = []
        for req in request_list:
            req_str = hash_fn(req)
            if req_str not in compressed:
                compressed.append(req)
        return compressed
