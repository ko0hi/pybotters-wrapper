import unittest

import pytest

import pybotters
import pybotters_wrapper as pbw

from pybotters_wrapper._apis import EXCHANGE2STORE, EXCHANGE2API
from pybotters_wrapper.sandbox import SandboxDataStoreWrapper, SandboxAPI


@pytest.mark.asyncio
async def test_create_store_and_api(
    testcase: unittest.TestCase, client: pybotters.Client
):
    for k in EXCHANGE2STORE.keys():
        store, api = pbw.create_store_and_api(k, client)
        testcase.assertIsInstance(store, EXCHANGE2STORE[k])
        testcase.assertIsInstance(api, EXCHANGE2API[k])


@pytest.mark.asyncio
async def test_create_store_and_api_sandbox(
    testcase: unittest.TestCase, client: pybotters.Client
):
    for k in EXCHANGE2STORE.keys():
        store, api = pbw.create_store_and_api(k, client, sandbox=True)
        testcase.assertIsInstance(store, SandboxDataStoreWrapper)
        testcase.assertIsInstance(api, SandboxAPI)
        testcase.assertIsInstance(store._simulate_store, EXCHANGE2STORE[k])
        testcase.assertIsInstance(api._simulate_api, EXCHANGE2API[k])


@pytest.mark.asyncio
async def test_exchange_create_store_and_api(
    testcase: unittest.TestCase, client: pybotters.Client
):
    for k in EXCHANGE2STORE.keys():
        store, api = getattr(pbw, f"create_{k}_store_and_api")(client)
        testcase.assertIsInstance(store, EXCHANGE2STORE[k])
        testcase.assertIsInstance(api, EXCHANGE2API[k])
