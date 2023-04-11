import os
import unittest

import pandas as pd
import pytest

from pybotters_wrapper.plugins.influxdb import InfluxDB

token, org, bucket = "pbw", "pbw", "pbw_test"


@pytest.fixture()
def influx():
    return InfluxDB(token, org, bucket)


@pytest.fixture()
def create_test_bucket():
    _influx = InfluxDB(token, org, bucket)
    _bucket = _influx.create_bucket(delete=True)
    yield
    _influx.client(sync=True).buckets_api().delete_bucket(_bucket.id)


@pytest.mark.skipif(
    not os.environ.get("PBW_TEST_PLUGIN_INFLUXDB", None),
    reason="require special settings for testing the InfluxDB plugin",
)
def test_create_bucket_if_not_exist(testcase: unittest.TestCase):
    params = dict(url="http://localhost:8086", token="pbw", org="pbw")
    from influxdb_client import InfluxDBClient
    client = InfluxDBClient(**params)
    api = client.buckets_api()
    test_bucket = str(pd.Timestamp.utcnow().timestamp())
    _bucket = api.find_bucket_by_name(test_bucket)
    testcase.assertIsNone(_bucket)
    InfluxDB(token, org, test_bucket)
    _bucket = api.find_bucket_by_name(test_bucket)
    testcase.assertIsNotNone(_bucket)


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.environ.get("PBW_TEST_PLUGIN_INFLUXDB", None),
    reason="require special settings for testing the InfluxDB plugin",
)
async def test_write_execution(
    testcase: unittest.TestCase, influx: InfluxDB, create_test_bucket
):
    timestamp = pd.Timestamp.utcnow()
    await influx.write_execution("test", "1", "BTCUSDT", "BUY", 20000, 2, timestamp)
    res = (
        influx.client(sync=True)
        .query_api()
        .query(f'from(bucket: "pbw_test") |> range(start: 0)')
    )

    testcase.assertEqual(2, len(res))
    testcase.assertEqual(1, len(res[0].records))
    testcase.assertDictEqual(
        {
            "_measurement": "test",
            "_time": pd.to_datetime(timestamp).to_pydatetime(),
            "_value": 20000,
            "_field": "price",
            "id": "1",
            "symbol": "BTCUSDT",
            "side": "BUY",
        },
        {
            k: v
            for (k, v) in res[0].records[0].values.items()
            if k not in ("result", "table", "_start", "_stop")
        },
    )
    testcase.assertEqual(1, len(res[1].records))
    testcase.assertDictEqual(
        {
            "_measurement": "test",
            "_time": pd.to_datetime(timestamp).to_pydatetime(),
            "_value": 2,
            "_field": "size",
            "id": "1",
            "symbol": "BTCUSDT",
            "side": "BUY",
        },
        {
            k: v
            for (k, v) in res[1].records[0].values.items()
            if k not in ("result", "table", "_start", "_stop")
        },
    )
