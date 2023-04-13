import pytest
from typing import Any


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
