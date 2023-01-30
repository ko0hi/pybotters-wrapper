import pytest

from unittest import TestCase


@pytest.fixture
def testcase() -> TestCase:
    testcase = TestCase()
    testcase.maxDiff = None
    return testcase
