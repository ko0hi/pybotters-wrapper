import pytest
import pytest_asyncio

from unittest import TestCase


import pybotters
import pybotters_wrapper as pbw


@pytest.fixture
def testcase() -> TestCase:
    testcase = TestCase()
    testcase.maxDiff = None
    return testcase


@pytest_asyncio.fixture
async def client() -> pybotters.Client:
    return pbw.create_client()
