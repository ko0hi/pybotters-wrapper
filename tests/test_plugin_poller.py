import asyncio
import unittest

import pybotters
import pytest
import pytest_mock

import pybotters_wrapper as pbw


@pytest.mark.asyncio
async def test_poller(
    testcase: unittest.TestCase,
    client: pybotters.Client,
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch(
        "pybotters_wrapper.core.api.API.request", return_value=None
    )

    api = pbw.create_binanceusdsm_api(client)

    async def handler(item):
        raise RuntimeError

    poller = pbw.plugins.poller(
        api,
        interval=1,
        url="/api/dummy",
        handler=handler,
    )

    spy = mocker.spy(poller, '_handle')

    await asyncio.sleep(1)

    initial_call_count = spy.call_count
    testcase.assertTrue(spy.called)
    testcase.assertFalse(poller.task.done())

    poller.stop()

    await asyncio.sleep(1)
    testcase.assertEqual(initial_call_count, spy.call_count)
    testcase.assertTrue(poller.task.cancelled())
