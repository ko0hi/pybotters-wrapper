from typing import Any, Callable

import pybotters
import pytest
import pytest_mock
from aioresponses import aioresponses
from pybotters.store import StoreChange

from pybotters_wrapper import create_client
from pybotters_wrapper.core import (
    FetchAPI,
    NormalizedStoreBuilder,
    TickerFetchAPI,
    OrderbookFetchAPI,
    OrdersFetchAPI,
    PositionsFetchAPI,
    OrderAPI,
    LimitOrderAPI,
    MarketOrderAPI,
    CancelOrderAPI,
    StopLimitOrderAPI,
    StopMarketOrderAPI,
)


# disable logging: https://github.com/Delgan/loguru/issues/138
from loguru import logger

logger.remove(0)


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
            return MockAsyncResponse(self._url, self._response)

        return _mock_async_request


@pytest.fixture
def async_response_mocker():
    def factory(sample_response: Any, status: int = 200):
        return MockAsyncResponse(sample_response, status)

    return factory


class FetchAPITester:
    _API_CLASS = None
    _FETCH_METHOD = None

    def __init__(
        self,
        *,
        symbol: str,
        url: str,
        factory_method: Callable[[pybotters.Client], FetchAPI],
        dummy_response: Any,
        expected_generate_endpoint: str,
        expected_translate_parameters: dict,
        expected_itemize_response: dict,
    ):
        self.symbol = symbol
        self.url = url
        self.factory_method = factory_method
        self.dummy_response = dummy_response
        self.expected_generate_endpoint = expected_generate_endpoint
        self.expected_translate_parameters = expected_translate_parameters
        self.expected_itemize_response = expected_itemize_response

    async def test_fetch(self):
        async with create_client() as client:
            resp = await client.get(self.url)
            assert resp.status == 200
            data = await resp.json()
            return resp, data

    async def test_api(self):
        async with create_client() as client:
            api = self.factory_method(client)
            return await getattr(api, self._FETCH_METHOD)(self.symbol)  # type: ignore

    async def test_generate_endpoint(self):
        async with create_client() as client:
            api = self.factory_method(client)
            actual = api._generate_endpoint({"symbol": self.symbol, "extra_params": {}})
            assert actual == self.expected_generate_endpoint

    async def test_translate_parameters(self):
        async with create_client() as client:
            api = self.factory_method(client)
            actual = api._translate_parameters(
                {
                    "endpoint": self.expected_generate_endpoint,
                    "symbol": self.symbol,
                    "extra_params": {},
                }
            )

            assert actual == self.expected_translate_parameters

    async def test_itemize_response(self):
        async with create_client() as client:
            with aioresponses() as m:
                m.get(self.url, payload=self.dummy_response)
                resp = await client.get(self.url)
                resp_data = await resp.json()
                api = self.factory_method(client)

                actual = api._itemize_response(resp, resp_data)

                assert actual == self.expected_itemize_response

    async def test_combined(self, mocker: pytest_mock.MockerFixture):
        spy_generate_endpoint = mocker.spy(self._API_CLASS, "_generate_endpoint")
        spy_translate_parameters = mocker.spy(self._API_CLASS, "_translate_parameters")
        spy_itemize_response = mocker.spy(self._API_CLASS, "_itemize_response")
        async with create_client() as client:
            api = self.factory_method(client)
            with aioresponses() as m:
                m.get(self.url, payload=self.dummy_response)
                await getattr(api, self._FETCH_METHOD)(self.symbol)

                assert (
                    spy_generate_endpoint.spy_return == self.expected_generate_endpoint
                )
                assert (
                    spy_translate_parameters.spy_return
                    == self.expected_translate_parameters
                )
                assert spy_itemize_response.spy_return == self.expected_itemize_response


@pytest.fixture
def ticker_fetch_api_tester():
    class TickerFetchAPITester(FetchAPITester):
        _API_CLASS = TickerFetchAPI
        _FETCH_METHOD = "fetch_ticker"

    return TickerFetchAPITester


@pytest.fixture
def orderbook_fetch_api_tester():
    class OrderbookFetchAPITester(FetchAPITester):
        _API_CLASS = OrderbookFetchAPI
        _FETCH_METHOD = "fetch_orderbook"

    return OrderbookFetchAPITester


@pytest.fixture
def orders_fetch_api_tester():
    class OrdersFetchAPITester(FetchAPITester):
        _API_CLASS = OrdersFetchAPI
        _FETCH_METHOD = "fetch_orders"

    return OrdersFetchAPITester


@pytest.fixture
def positions_fetch_api_tester():
    class PositionsFetchAPITester(FetchAPITester):
        _API_CLASS = PositionsFetchAPI
        _FETCH_METHOD = "fetch_positions"

    return PositionsFetchAPITester


class OrderAPITester:
    _API_CLASS = None
    _ORDER_METHOD = None

    def __init__(
        self,
        *,
        url: str,
        factory_method: Callable[[pybotters.Client], OrderAPI],
        request_method: str,
        dummy_order_parameters: dict,
        dummy_response: Any,
        expected_generate_endpoint: str,
        expected_translate_parameters: dict,
        expected_order_id: dict,
    ):
        self.url = url
        self.request_method = request_method
        self.factory_method = factory_method
        self.dummy_order_parameters = dummy_order_parameters
        self.dummy_response = dummy_response
        self.expected_generate_endpoint = expected_generate_endpoint
        self.expected_translate_parameters = expected_translate_parameters
        self.expected_order_id = expected_order_id

    async def test_order(self):
        async with create_client() as client:
            api = self.factory_method(client)
            return await getattr(api, self._ORDER_METHOD)(**self.dummy_order_parameters)

    async def test_api(self):
        async with create_client() as client:
            api = self.factory_method(client)
            return await getattr(api, self._ORDER_METHOD)(**self.dummy_order_parameters)  # type: ignore

    async def test_generate_endpoint(self):
        async with create_client() as client:
            api = self.factory_method(client)
            actual = api._generate_endpoint(self.dummy_order_parameters)
            assert actual == self.expected_generate_endpoint

    async def test_translate_parameters(self):
        async with create_client() as client:
            api = self.factory_method(client)
            actual = api._translate_parameters(
                {
                    "endpoint": self.expected_generate_endpoint,
                    **self.dummy_order_parameters,
                }
            )
            assert actual == self.expected_translate_parameters

    async def test_extract_order_id(self):
        async with create_client() as client:
            api = self.factory_method(client)
            actual = api._extract_order_id(
                MockAsyncResponse(self.url, self.dummy_response, 200),  # type: ignore
                self.dummy_response,  # noqa
            )
            assert actual == self.expected_order_id

    async def test_combined(self, mocker: pytest_mock.MockerFixture):
        spy_generate_endpoint = mocker.spy(self._API_CLASS, "_generate_endpoint")
        spy_translate_parameters = mocker.spy(self._API_CLASS, "_translate_parameters")
        spy_wrap_response = mocker.spy(self._API_CLASS, "_wrap_response")

        async with create_client() as client:
            api = self.factory_method(client)
            with aioresponses() as m:
                getattr(m, self.request_method.lower())(
                    self.url, payload=self.dummy_response
                )
                await getattr(api, self._ORDER_METHOD)(**self.dummy_order_parameters)

                assert (
                    spy_generate_endpoint.spy_return == self.expected_generate_endpoint
                )
                assert (
                    spy_translate_parameters.spy_return
                    == self.expected_translate_parameters
                )
                assert spy_wrap_response.spy_return.order_id == self.expected_order_id


@pytest.fixture
def limit_order_tester():
    class LimitOrderAPITester(OrderAPITester):
        _API_CLASS = LimitOrderAPI
        _ORDER_METHOD = "limit_order"

    return LimitOrderAPITester


@pytest.fixture
def market_order_tester():
    class MarketOrderAPITester(OrderAPITester):
        _API_CLASS = MarketOrderAPI
        _ORDER_METHOD = "market_order"

    return MarketOrderAPITester


@pytest.fixture
def cancel_order_tester():
    class CancelOrderAPITester(OrderAPITester):
        _API_CLASS = CancelOrderAPI
        _ORDER_METHOD = "cancel_order"

    return CancelOrderAPITester


@pytest.fixture
def stop_limit_order_tester():
    class StopLimitOrderAPITester(OrderAPITester):
        _API_CLASS = StopLimitOrderAPI
        _ORDER_METHOD = "stop_limit_order"

    return StopLimitOrderAPITester


@pytest.fixture
def stop_market_order_tester():
    class StopMarketOrderAPITester(OrderAPITester):
        _API_CLASS = StopMarketOrderAPI
        _ORDER_METHOD = "stop_market_order"

    return StopMarketOrderAPITester


class NormalizedStoreTester:
    _STORE_NAME: str | None = None

    def __init__(
        self,
        *,
        builder_factory_method: Callable[[], NormalizedStoreBuilder],
        dummy_data: dict,
        expected_item: dict,
    ):
        self.builder_factory_method = builder_factory_method
        self.dummy_change_insert = StoreChange(None, "insert", {}, dummy_data)
        self.dummy_change_update = StoreChange(None, "update", {}, dummy_data)
        self.dummy_change_delete = StoreChange(None, "delete", {}, dummy_data)
        self.expected_item = expected_item

    def get_store(self):
        assert self._STORE_NAME is not None
        return self.builder_factory_method().get(self._STORE_NAME)

    def test_insert(self):
        store = self.get_store()
        store._on_watch(self.dummy_change_insert)
        assert len(store) == 1

    def test_update(self):
        store = self.get_store()
        store._on_watch(self.dummy_change_update)
        assert len(store) == 1

    def test_delete(self):
        store = self.get_store()
        store._on_watch(self.dummy_change_insert)
        store._on_watch(self.dummy_change_delete)
        assert len(store) == 0

    def test_item(self):
        store = self.get_store()
        store._on_watch(self.dummy_change_insert)
        item = store.find()[0]
        item.pop("info")
        assert item == self.expected_item


@pytest.fixture
def ticker_normalized_store_tester():
    class TickerNormalizedStoreTester(NormalizedStoreTester):
        _STORE_NAME = "ticker"

    return TickerNormalizedStoreTester


@pytest.fixture
def trades_normalized_store_tester():
    class TradesNormalizedStoreTester(NormalizedStoreTester):
        _STORE_NAME = "trades"

    return TradesNormalizedStoreTester


@pytest.fixture
def orderbook_normalized_store_tester():
    class OrderbookNormalizedStoreTester(NormalizedStoreTester):
        _STORE_NAME = "orderbook"

    return OrderbookNormalizedStoreTester


@pytest.fixture
def order_normalized_store_tester():
    class OrderNormalizedStoreTester(NormalizedStoreTester):
        _STORE_NAME = "order"

    return OrderNormalizedStoreTester


@pytest.fixture
def position_normalized_store_tester():
    class PositionNormalizedStoreTester(NormalizedStoreTester):
        _STORE_NAME = "position"

    return PositionNormalizedStoreTester


@pytest.fixture
def execution_normalized_store_tester():
    class ExecutionNormalizedStoreTester(NormalizedStoreTester):
        _STORE_NAME = "execution"

    return ExecutionNormalizedStoreTester
