import pytest
from typing import Any
import os
import json


@pytest.fixture
def resources_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "./resources")


@pytest.fixture
def resource_loader(resources_dir):
    def wrapper(filename: str) -> any:
        filepath = os.path.join(resources_dir, filename)
        if filepath.endswith(".json"):
            with open(filepath) as f:
                return json.load(f)
        else:
            raise RuntimeError(f"Unsupported file type: {filename}")

    return wrapper


@pytest.fixture
def async_response_mocker():
    class MockAsyncResponse:
        def __init__(self, url: str, response: Any, status: int = 200):
            self._url = url
            self._response = response
            self._status = status

        async def json(self):
            return self._response

        @property
        def status(self):
            return self._status

        def as_request_method(self):
            async def _mock_async_request(*args, **kwargs):
                return MockAsyncResponse(self._response)

            return _mock_async_request

    def factory(sample_response: Any, status: int = 200):
        return MockAsyncResponse(sample_response, status)

    return factory
